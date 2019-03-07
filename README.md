# scripts
General purpose scripts

<b>bagcheck.py</b>

Recursive bulk bag validation. Saves validation results in a json file at the base directory. Will report on new bags added to the directory and bags that are missing since the previous scan. --report option will print to cl the last validation for each bag and how long it's been since last checked.

Installation

python 3 required

::

  pip install bagit

clone, copy or download the script to a local destination.

Command Line Usage
------------------

::

    python bagcheck.py  /directory/with/bagsinit

Will recursively search through the directory identify and validating bags, finally saving the results to the file 'bags.json' in the directory provided.

::

    python bagcheck.py  --baglist /path/to/baglist.json /directory/with/bagsinit

Will open the baglist specified if it exists or save the resulting baglist to that location. If the baglist already exists, the directory is not required as bagcheck uses the directory specified in the baglist.
