import bagit
import os
import json
import argparse
import datetime

def get_baglist():
    if os.path.exists('bags.json'):
        with open('bags.json') as f:
            baglist = json.loads(f.read())
    else:
        baglist = {'date created' : datetime.datetime.now().isoformat(), 'base directory' : os.getcwd(), 'bags': {}}
    return(baglist)

def find_bags(dir):
    bags = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file == 'bagit.txt':
                bags.append(root)
    return(bags)

def report(baglist):
    for bag, checks in baglist['bags'].items():
        latest = max([datetime.datetime.fromisoformat(d) for d in checks.keys()])
        interval = datetime.datetime.now()-latest
        print(bag, latest.isoformat(), checks[latest.isoformat()], "{i.days} days, {i.seconds} seconds".format(i=interval))

def validate(baglist):
    bags = find_bags(baglist['base directory'])
    for bagdir in bags:
        if bagdir not in baglist['bags'].keys():
            print('New bag: ', bagdir)
            baglist['bags'].update({bagdir : {}})
        bag = bagit.Bag(bagdir)
        try:
            bag.validate()
            print(bagdir, 'is valid')
            baglist['bags'][bagdir].update({datetime.datetime.now().isoformat() : 'VALID'})
        except bagit.BagValidationError as e:
            print(e)
            baglist['bags'][bagdir].update({datetime.datetime.now().isoformat() : e.message})
    missing = [bag for bag in baglist['bags'].keys() if bag not in bags]
    for bag in missing:
        print('Missing: ', bag)
    with open('bags.json', 'w') as f:
        f.write(json.dumps(baglist, indent=1))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate some bags')
    parser.add_argument('directory', metavar='i', type=str, help='the base directory with your bags')
    parser.add_argument('--report', action='store_true', help='report on latest validations')
    args = parser.parse_args()

    os.chdir(args.directory)
    baglist = get_baglist()
    if args.report:
        report(baglist)
    else:
        validate(baglist)
