import os
import bagit
import argparse
import difflib
from pprint import pprint
from io import StringIO
import csv


def filter_hashes(p_entries, alg, filter=None):
    '''
    Filter hashes to a specific directory.
    Intended for use with standard package structures.
    '''
    h = []
    for file, hashes in p_entries.items():
        if filter is not None:
            if file.startswith(os.path.normpath(filter)):
                h.append(hashes.get(alg))
        else:
            h.append(hashes.get(alg))
    return(h)


def rehash(bag, alg, filter=None):
    'generates a hash list if the two bags do not have matching algs'
    hashes = []
    os.chdir(bag.path)
    for root, _, files in os.walk(os.getcwd):
        for file in files:
            p = os.path.relpath(os.path.join(root, file))
            if filter is not None:
                if p.startswith(filter):
                    h = bagit.generate_manifest_lines(p, [alg])
                    hashes.append(h[1])
            else:
                h = bagit.generate_manifest_lines(p, [alg])
                hashes.append(h[1])
    return(hashes)


def compare_bags(a, b, filter=None):
    algorithm = None
    for alg in a.algorithms:
        if alg in b.algorithms:
            algorithm = alg
    a_hashes = filter_hashes(a.payload_entries(), algorithm, filter)
    if algorithm is None:
        b_hashes = rehash(b, a.algorithms[0], filter=filter)
    b_hashes = filter_hashes(b.payload_entries(), algorithm, filter)
    if a_hashes != [] and b_hashes != []:
        s = difflib.SequenceMatcher(None, a_hashes, b_hashes)
        return(s)


def breakdown(a, b, seq_matcher):
    csv_heads = [
        'Bag_1', 'filecount_1', 'Bag_2', 'filecount_2', 'Ratio',
        'matched_files', 'ratio of Bag_1 in Bag_2', 'ratio of Bag_2 in Bag_1']
    matches = 0
    blocks = seq_matcher.get_matching_blocks()
    len_a = blocks[-1][0]
    len_b = blocks[-1][1]
    for block in blocks:
        matches += block[2]
    line = [
        a.path, len_a, b.path, len_b, seq_matcher.ratio(), matches,
        matches/len_a, matches/len_b]
    line = dict(zip(csv_heads, line))
    return(line)


csv_heads = [
    'Bag_1', 'filecount_1', 'Bag_2', 'filecount_2', 'Ratio',
    'matched_files', 'ratio of Bag_1 in Bag_2', 'ratio of Bag_2 in Bag_1']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compare level of similarity of bagit packages')
    parser.add_argument(
        'bag', metavar='i', type=str, help='the path of bag to compare')
    parser.add_argument(
        'dir', metavar='d',
        help='bag for comparison or directory with bags in recursive mode')
    parser.add_argument(
        '--threshold', '-t', type=float, default=0.5,
        help='minimum level of similarity (only used in recursive mode).')
    parser.add_argument(
        '--filter', '-f',
        help='relative path (starting with "data")'
        ' if only a portion of the bag(s) are to be compared')
    parser.add_argument(
        '--recurse', '-r', action='store_true',
        help='walk through a directory finding and comparing bags')
    parser.add_argument(
        '--details', '-d', action='store_true',
        help='walk through a directory finding and comparing bags')

    args = parser.parse_args()
    bag_a = bagit.Bag(args.bag)

    if args.recurse:
        if args.details:
            csv_file = StringIO(newline='')
            writer = csv.DictWriter(csv_file, fieldnames=csv_heads)
            writer.writeheader()
        for root, _, files in os.walk(args.dir):
            if 'bagit.txt' in files and root != bag_a.path:
                bag_b = bagit.Bag(root)
                sm = compare_bags(bag_a, bag_b, filter=args.filter)
                if sm is not None:
                    score = sm.quick_ratio()
                    if score > args.threshold:
                        print(os.path.split(bag_b.path)[1], score)
                        if args.details:
                            d = breakdown(bag_a, bag_b, sm)
                            writer.writerow(d)
        if args.details:
            print(csv_file.getvalue())
    else:
        bag_b = bagit.Bag(args.dir)
        sm = compare_bags(bag_a, bag_b, filter=args.filter)
        if sm is not None:
            score = sm.quick_ratio()
            if args.details:
                print(
                    'Seq a: {0}, Seq b: {1}, Matching files: {2}'.format(*breakdown(sm)))
            print(os.path.split(bag_b.path)[1], score)
