import bagit
import os
import argparse
import shutil
import logging
from fnmatch import fnmatch


def payload_filter(bag, splitter):
    'splits a payload on a unix path expression, returning both halves'
    new_payload = {
        file: hash for file, hash in bag.payload_entries().items()
        if fnmatch(os.path.normpath(file), splitter)}
    old_payload = {
        file: hash for file, hash in bag.payload_entries().items()
        if file not in new_payload.keys()}
    return new_payload, old_payload


def move_files(payload_dict, dest):
    'move files from old bag to new'
    for file in payload_dict.keys():
        dirs = os.path.split(file)[0]
        destination = os.path.join(dest, dirs)
        if not os.path.exists(destination):
            os.makedirs(destination)
        logging.info('Copying {} to {}'.format(file, destination))
        shutil.copy2(file, destination)


def del_files(payload_dict):
    for file in payload_dict.keys():
        logging.info('Removing {}'.format(file))
        os.remove(file)


def write_manifests(payload_dict, algs, dest):
    size = 0
    for file, hash in payload_dict.items():
        if not os.path.exists(dest):
            os.makedirs(dest)
        size = size + os.path.getsize(file)
        for alg in algs:
            m_name = 'manifest-{}.txt'.format(alg)
            fname = os.path.join(dest, m_name)
            with open(fname, 'a', encoding='utf-8') as f:
                f.write("{}  {}\n".format(hash[alg], file))
    oxum = '{}.{}'.format(size, len(payload_dict))
    return oxum


def main(source, dest, splitter, partition=False):
    source_bag = bagit.Bag(source)
    new_payload, old_payload = payload_filter(source_bag, splitter)
    if len(new_payload) == 0:
        print('No files to split!')
        exit()
    if not os.path.exists(dest):
        os.mkdir(dest)
    os.chdir(source)
    new_oxum = write_manifests(new_payload, source_bag.algorithms, dest)
    move_files(new_payload, dest)
    logging.info('Writing manifests')
    if partition:
        for file in source_bag.manifest_files():
            os.remove(file)
        old_oxum = write_manifests(
            old_payload, source_bag.algorithms, source_bag.path)
    for file, hash in source_bag.tagfile_entries().items():
        if 'manifest' not in file:
            logging.info('Copying tag file {} to {}'.format(file, dest))
            shutil.copy(file, dest)
    new_bag = bagit.Bag(dest)
    new_bag.info['Payload-Oxum'] = new_oxum
    if partition:
        source_bag.info['Payload-Oxum'] = old_oxum
    new_bag.save()
    logging.info('Validating bag {}'.format(new_bag.path))
    if new_bag.validate() and partition:
        del_files(new_payload)
        source_bag.save()
    else:
        logging.error('bag {} is invalid'.format(new_bag.path))
    logging.info('Validating bag {}'.format(source_bag.path))
    source_bag.validate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='split a bagit package on a unix path expression')
    parser.add_argument(
        'source', metavar='i', help='the path of bag to split')
    parser.add_argument(
        'dest', metavar='o', help='new path for split files')
    parser.add_argument(
        '--splitter', '-s', dest='split', required=True,
        help='relative path (beginning with "data") to split bag on.'
        'Supports unix style pattern matching')
    parser.add_argument(
        '--partition', '-p', action='store_true',
        help='remove files from the source bag rather than just copying')

    args = parser.parse_args()
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s: %(message)s', level=logging.INFO)
    main(args.source, args.dest, args.split, partition=args.partition)
