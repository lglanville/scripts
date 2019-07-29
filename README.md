## Various scripts for working with bagit pakcages

Installation

python 3.7 required



    pip install bagit

clone, copy or download the script to a local destination.

#### bagcheck.py

Recursive bulk bag validation. Saves validation results in a json file at the base directory. Will report on new bags added to the directory and bags that are missing since the previous scan. --report option will print to cl the last validation for each bag and how long it's been since last checked.

Usage
------------------
```
python bagcheck.py  /directory/with/bagsinit
```
Will recursively search through the directory identify and validating bags, finally saving the results to the file 'bags.json' in the directory provided.

```
python bagcheck.py  --baglist /path/to/baglist.json /directory/with/bagsinit
```
Will open the baglist specified if it exists or save the resulting baglist to that location. If the baglist already exists, the directory is not required as bagcheck uses the directory specified in the baglist.

#### bag_split.py
Split a bag using a unix path expression. Checksum are transferred between the original and new bag and both bags are validated on exit.

Usage
------------------

```
python bag_split.py  /original_bag /new_bag --split data/directory*
```
#### bag_compare.py
Uses difflib to compare relative similarity between bags.

Usage
------------------
```
python bag_compare.py  /bag_one /bag_two
```
or recursive:
```
python bag_compare.py -r /bag_one /directory/with/bagsinit
```
