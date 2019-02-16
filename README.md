# ddr-iaconvert
Converts DDR csv metadata into IA's cli upload csv format.

This script converts DDR metadata into a CSV file formatted for use with Internet 
Archive's (IA) command-line upload tool (https://github.com/jjjake/internetarchive). 
The command examines a given directory of DDR binary files and associated metadata 
CSV file that has been exported from the DDR system.

## Requirements

Compatible with Python 3 only. Requires `simplejson`, `jinja2` and `dateutil`.

## Usage

`ddr-iaconvert.py [-h] entitycsv filecsv`

**Positional Arguments:**
```
  entitycsv   Absolute path to DDR entities csv file.
  filecsv     Absolute path to DDR files csv file.
```

**Optional Arguments:**
```
  -h, --help  show this help message and exit
```

**Examples**:
```
     $ ddr-iaconvert ./ddr-densho-1-entities.csv ./ddr-densho-1-files.csv
```

### Notes and Tips

1. The script traverses all of the entries in the input files csv, then for 
each that is marked as `external`, it attempts to match against the 
entities input file to pull associated metadata.

2. The script uses the `format` attribute to determine whether an entity is 
a DDR visual history. If so, it performs additional processing to link 
together segments and add other VH-related info to the IA metadata.

3. In order to properly process VH materials, all segment entities and the 
parent interview entity must be present in the input entities csv. In 
addition, the `sort` attribute must contain the actual segment number. 