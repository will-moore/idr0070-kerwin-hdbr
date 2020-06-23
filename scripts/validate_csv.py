import csv
import os
import argparse
import glob
import sys

"""
This reads the first .csv metadata file found in cwd()/20200214-ftp
Checks that files listed in the csv exist under path_to_data/20200214-ftp
Also checks that files found in path_to_data/20200214-ftp are listed in the csv

We need to run this with access to the submitted files at path_to_data.

Usage: run from the idr0070-kerwin-hdbr root dir with each 'batch' dir in turn:
e.g.
$ python scripts/validate.csv 20191021-original
"""

parser = argparse.ArgumentParser()
parser.add_argument('batch_dir')
args = parser.parse_args(sys.argv[1:])

print('batch_dir', args.batch_dir)
project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr"

# Batch1 example - NB: extra HDBR_PAX6 directory - handle below...
# 20191021-original/HDBR_PAX6/10PCW_IHC_coronal/10pcw_1677_3_019_2_pax6.jpg
# Batch2 example
# 20200214-ftp/HDBR_CITED2_ISH/10794,1,embryo,CS20,58_2014-07-07 16_12_49.scn
# Batch3 example
# 20200414-Batch3-ftp/HDBR_FGFR3_CS22_ISH_hires/ImageCollection_0000001679_2012-10-01 13_54_32.scn

batch_dir = args.batch_dir
if batch_dir == "20191021-original":
    batch_dir = "20191021-original/HDBR_PAX6"

path_to_data = os.path.join(path_to_data, batch_dir)
print('path_to_data', path_to_data)

# Find csv file in dir...
path_to_csv = os.path.join(os.getcwd(), 'experimentA', args.batch_dir)
csv_files = glob.glob(os.path.join(path_to_csv, "*.csv"))
print('csv_files', path_to_csv, csv_files)

found = []
not_found = []
print("Reading CSV...", csv_files[0])
with open(csv_files[0], mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    gene_col_index = 0

    for row in csv_reader:
        # ignore first row of CSV (column names)
        if line_count == 0:
            # print('Column names...')
            # print(row)
            gene_col_index = row.index("Comment [Gene Symbol]")
            line_count += 1
            continue

        # Read the columns we need...
        dir_name = row[0].strip()
        # batch1 has extra 'PAX6_'
        if 'PAX6' in batch_dir:
            dir_name = dir_name.replace("PAX6_", "")
        img_name = row[1]
        if len(dir_name) == 0:
            continue
        # gene = row[gene_col_index]

        # image_path = "%s/HDBR_%s/%s/%s" % (path_to_data, gene, dir_name, img_name)
        image_path = "%s/%s/%s" % (path_to_data, dir_name, img_name)

        # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
        new_name = "%s/%s" % (dir_name, img_name)

        # check we're creating correct paths
        if not os.path.exists(image_path):
            print(image_path)
            not_found.append(image_path)
            continue
        found.append(image_path)

        line_count += 1
    print("Not found on disk: ", len(not_found))

found_lowercase = [f.lower() for f in found]

print("\nReading images on disk...")
# iterate all images to find which are not listed above...
exts = ['jpg', 'mpg', 'svs', 'scn', 'gif']
not_found = []
for root, dirs, files in os.walk(path_to_data):
    archive_root = os.path.relpath(root, path_to_data)
    for f in files:
        fullpath = os.path.join(root, f)
        if fullpath not in found and f.split('.')[-1] in exts:
            print(fullpath, " (on disk, not in csv)")
            not_found.append(fullpath)
            # Check if it's only a case-sensitive mismatch:
            if fullpath.lower() in found_lowercase:
                idx = found_lowercase.index(fullpath.lower())
                print(found[idx].replace(path_to_data, ""), " (in csv)")
            print("\n")

print("Not found in CSV: ", len(not_found))
