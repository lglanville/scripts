import bagit
import os
import json
import argparse
import datetime

def get_baglist(filepath, *args):
    if os.path.exists(filepath):
        with open(filepath) as f:
            baglist = json.loads(f.read())
    else:
        baglist = {'date created' : datetime.datetime.now().isoformat(), 'base directory' : args[0], 'bags': {}}
    return(baglist)

def find_bags(baglist):
    bags = []
    for root, _, files in os.walk(baglist['base directory']):
        for file in files:
            if file == 'bagit.txt':
                bags.append(os.path.relpath(root, start=baglist['base directory']))
    return(bags)

def report(baglist):
    print(', '.join(['directory', 'check_date', 'check_status', 'details', 'since_last_check']))
    for bag, checks in baglist['bags'].items():
        latest = datetime.datetime.fromisoformat(checks[-1]['date'])
        interval = datetime.datetime.now()-latest
        print(', '.join([bag, latest.isoformat(), checks[-1]['status'], str(checks[-1].get('details')), "{i.days} days since last check".format(i=interval)]))

def validate(baglist, baglistfile):
    bags = find_bags(baglist)
    for bagdir in bags:
        if bagdir not in baglist['bags'].keys():
            print('New bag: ', bagdir)
            baglist['bags'].update({bagdir : []})
        try:
            bag = bagit.Bag(os.path.join(baglist['base directory'], bagdir))
            bag.validate()
            print(bagdir, 'is valid')
            baglist['bags'][bagdir].append({'date': datetime.datetime.now().isoformat(), 'status' : 'VALID'})
        except (bagit.BagError, bagit.BagValidationError) as e:
            print(e)
            if hasattr(e, 'message'):
                e = e.message
            else:
                e = e.args[0]
            baglist['bags'][bagdir].append({'date' : datetime.datetime.now().isoformat(), 'status' : 'INVALID', 'details': e})
    missing = [bag for bag in baglist['bags'].keys() if bag not in bags]
    for bag in missing:
        print('Missing: ', bag)
        baglist['bags'][bag].append({date: datetime.datetime.now().isoformat(), 'status' : 'MISSING'})
    with open(baglistfile, 'w') as f:
        f.write(json.dumps(baglist, indent=1))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate some bags.')
    parser.add_argument('directory', metavar='i', type=str, nargs='?', help='the base directory with your bags. Not required if using an existing baglist')
    parser.add_argument('--baglist', dest='baglist', type=str, default='bags.json', help='Location of a new or existing bag list. If it already exists, directory will be ignored in favor of the base directory defined in the list.')
    parser.add_argument('--report', action='store_true', help='report on latest validations in csv (pipe to a text file)')
    args = parser.parse_args()

    if args.directory != None:
        os.chdir(args.directory)
    baglist = get_baglist(args.baglist, args.directory)
    os.chdir(baglist['base directory'])
    if args.report:
        report(baglist)
    else:
        validate(baglist, args.baglist)
