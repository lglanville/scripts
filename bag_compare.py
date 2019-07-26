import os
import bagit
import argparse
import difflib


def filter_hashes(p_entries, alg, filter=None):
    """
    Filter hashes to a specific directory.
    Intended for use with standard package structures.
    """
    h = []
    for file, hashes in p_entries.items():
        if filter is not None:
            if file.startswith(os.path.normpath(filter)):
                h.append(hashes.get(alg))
        else:
            h.append(hashes.get(alg))
    return(h)


def compare_bags(a, b, filter=None):
    for alg in a.algorithms:
        if alg in b.algorithms:
            algorithm = alg
    a_hashes = filter_hashes(a.payload_entries(), algorithm, filter)
    b_hashes = filter_hashes(b.payload_entries(), algorithm, filter)
    if a_hashes != [] and b_hashes != []:
        s = difflib.SequenceMatcher(None, a_hashes, b_hashes)
        return(s)


def breakdown(seq_matcher):
    matches = 0
    blocks = seq_matcher.get_matching_blocks()
    len_a = blocks[-1][0]
    len_b = blocks[-1][1]
    for block in blocks:
        matches += block[2]
    return([len_a, len_b, matches])


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
        for root, _, files in os.walk(args.dir):
            if 'bagit.txt' in files and root != bag_a.path:
                bag_b = bagit.Bag(root)
                sm = compare_bags(bag_a, bag_b, filter=args.filter)
                if sm is not None:
                    score = sm.quick_ratio()
                    if score > args.threshold:
                        print(os.path.split(bag_b.path)[1], score)
                        if args.details:
                            a, b, m = breakdown(sm)
                            print(
                                f'Total files matched: {m}\n'
                                f'{os.path.split(bag_a.path)[1]}: {a} '
                                f'total files ({int((m/a)*100)}% matched)\n'
                                f'{os.path.split(bag_b.path)[1]}: {b} '
                                f'total files ({int((m/b)*100)}% matched)')

    else:
        bag_b = bagit.Bag(args.dir)
        sm = compare_bags(bag_a, bag_b, filter=args.filter)
        if sm is not None:
            score = sm.quick_ratio()
            if args.details:
                print(
                    'Seq a: {0}, Seq b: {1}, Matching files: {2}'.format(*breakdown(sm)))
            print(os.path.split(bag_b.path)[1], score)
