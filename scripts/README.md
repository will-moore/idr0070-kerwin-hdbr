
Scripts workflow
================

The scripts in this directory were used in the following workflow:

 - validate_csv.py used initially to check we have all files listed in the csvs
 - csv_to_bulk.py used to generate bulk import filePaths.tsv
 - After importing, use validate_imports.py to check and create file-names csv
 - csv_to_annotations.py uses the file-names csv to create annotations.csv
 - Use idr0070-mpg-upload.py to in-place upload mpg files to Datasets
 