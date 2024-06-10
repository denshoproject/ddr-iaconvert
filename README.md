**This project has been replaced by `DDR.cli.ddriaconvert`: https://github.com/denshoproject/ddr-cmdln/blob/develop/ddr/DDR/cli/ddriaconvert.py**

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
  entitycsv            Absolute path to DDR entities csv file.
  filecsv              Absolute path to DDR files csv file.
  outputpath           Path to save output.
  binariespath         Path to original binaries for prep.
```

**Optional Arguments:**
```
  -h, --help  show this help message and exit
  -b, --prep-binaries  Prep binaries for upload. Uses binariespath argument.
```

**Examples**:
```
  $ ddr-iaconvert.py ./ddr-densho-1-entities.csv ./ddr-densho-1-files.csv
  $ ddr-iaconvert.py -b ./ddr-entities.csv ./ddr-files.csv ./output/ ./binaries-in/
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

4. The `id` column in the files input csv may contain either the 
identifier of the file (e.g., `ddr-densho-1-2-master-400ff321a5`) or the 
identifier of the parent entity (e.g., `ddr-densho-1-2`). In the former 
case, the csv would have been generated with the `ddrexport` command; 
the latter would be a csv used to batch ingest binaries with the 
`ddrimport` command.
