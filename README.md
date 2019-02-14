# ddr-iaconvert
Converts DDR csv metadata into IA's cli upload csv format.

This command converts DDR metadata into a CSV file formatted for use with Internet 
Archive's (IA) command-line upload tool (https://github.com/jjjake/internetarchive). 
The command examines a given directory of DDR binary files and associated metadata 
CSV file that has been exported from the DDR system.

## Requirements

Compatible with Python 3 only. Requires `simplejson`, `jinja2` and `dateutil`

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

