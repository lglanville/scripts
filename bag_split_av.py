import bagit
import os
import argparse
import shutil
import logging
from fnmatch import fnmatch


def payload_filter(bag, number):
    'splits a payload on an item number, returning both halves'
    new_payload = {
        file: hash for file, hash in bag.payload_entries().items()
        if fnmatch(os.path.normpath(file), f'*{number}*')}
    old_payload = {
        file: hash for file, hash in bag.payload_entries().items()
        if file not in new_payload.keys()}
    return new_payload, old_payload


def move_files(payload_dict, dest, number):
    'move files from old bag to new'
    newpayload = {}
    size = 0
    for file, hash in payload_dict.items():
        if number in os.path.split(file)[1]:
            if file.endswith('.imx.mxf'):
                ext = 'production'
                destination = os.path.join(dest, 'data', ext)
            elif file.endswith('.mxf'):
                ext = 'preservation'
                destination = os.path.join(dest, 'data', ext)
            elif file.endswith('.mp4'):
                ext = 'access'
                destination = os.path.join(dest, 'data', ext)
            else:
                ext = 'metadata/submissionDocumentation'
                destination = os.path.join(dest, 'data', ext)
        else:
            dirs = file.split('\\')
            for count, d in enumerate(dirs):
                if number in d:
                    path = '\\'.join(dirs[count:len(dirs)-1])
                    break
            destination = os.path.join(dest, 'data/preservation', path)
        newpath = os.path.join(destination, os.path.split(file)[1])
        newpayload[os.path.relpath(newpath, start=dest)] = hash
        if not os.path.exists(destination):
            os.makedirs(destination)
        logging.info('Copying {} to {}'.format(file, destination))
        shutil.copy2(file, destination)
        size += os.path.getsize(file)
    oxum = oxum = f'{size}.{len(newpayload)}'
    return oxum, newpayload


def write_manifests(payload_dict, algs, dest):
    for file, hash in payload_dict.items():
        if not os.path.exists(dest):
            os.makedirs(dest)
        for alg in algs:
            m_name = 'manifest-{}.txt'.format(alg)
            fname = os.path.join(dest, m_name)
            with open(fname, 'a', encoding='utf-8') as f:
                f.write("{}  {}\n".format(hash[alg], file))


def main(source, dest, number):
    source_bag = bagit.Bag(source)
    new_payload, old_payload = payload_filter(source_bag, number)
    if len(new_payload) == 0:
        print('No files to split!')
        exit()
    if not os.path.exists(dest):
        os.mkdir(dest)
    os.chdir(source)
    new_oxum, new_payload = move_files(new_payload, dest, number)
    write_manifests(new_payload, source_bag.algorithms, dest)
    logging.info('Writing manifests')
    for file, hash in source_bag.tagfile_entries().items():
        if 'manifest' not in file:
            logging.info('Copying tag file {} to {}'.format(file, dest))
            shutil.copy(file, dest)
    new_bag = bagit.Bag(dest)
    new_bag.info['Payload-Oxum'] = new_oxum
    new_bag.info['identifier'] = number
    new_bag.save()
    logging.info('Validating bag {}'.format(new_bag.path))
    if not new_bag.validate():
        logging.error('bag {} is invalid'.format(new_bag.path))
    logging.info('Validating bag {}'.format(source_bag.path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='split files matching an item number from a bagit package')
    parser.add_argument(
        'source', metavar='i', help='the path of bag to split')
    parser.add_argument(
        'dest', metavar='o', help='new path for split files')
    parser.add_argument(
        '--number', '-n', dest='split', required=True,
        help='item number to split bag on.')

    args = parser.parse_args()
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s: %(message)s', level=logging.INFO)
    main(args.source, args.dest, args.split)
