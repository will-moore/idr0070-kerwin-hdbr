import csv
import os
import glob

"""
This script uses annotation csv files for each of the batch of files uploaded.
It combines them into a single 'idr0070-experimentA-filePaths.tsv'
for bulk import.

It creates a Dataset name for each image, based on the format:
'gene-stage', where gene and stage are read from the csv.

Usage: run from the idr0070-kerwin-hdbr root dir:
$ python scripts/csv_to_bulk_tsv.py

"""

project_name = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr"

batch_dirs = [
    '20200214-ftp', '20191021-original', '20200414-Batch3-ftp',
    '20200422-Batch5', '20200417-Batch4', '20200423-Batch6'
]

# Read the csv file from each batch, adding to single list of rows.
csv_rows = []
for dir_name in batch_dirs:
    # Find csv file in each dir...
    path_to_csv = os.path.join(os.getcwd(), 'experimentA', dir_name)
    csv_files = glob.glob(os.path.join(path_to_csv, "*.csv"))
    print('csv_files', path_to_csv, csv_files)
    assert len(csv_files) == 1

    with open(csv_files[0], mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        for r in rows:
            # print(r)
            assert r['Dataset Name'] is not None
            assert r["Image Name"] is not None
            assert r["Characteristics [Developmental Stage]"]
            assert r['Comment [Gene Symbol]']
            assert r['Comment [Image File Path]']
            r['batch_dir'] = dir_name
        # Ignore first row (column names)
        csv_rows.extend(rows[:])
        print(dir_name, len(rows), 'rows')


with open('idr0070-experimentA-filePaths.tsv', mode='w') as tsv_file:
    tsv_writer = csv.writer(tsv_file, delimiter='\t')

    for row in csv_rows:
        # Read the columns we need...
        dir_name = row['Dataset Name']
        img_name = row["Image Name"]
        stage = row["Characteristics [Developmental Stage]"]
        gene = row['Comment [Gene Symbol]']
        file_path = row['Comment [Image File Path]']

        batch_dir = row['batch_dir']
        image_path = os.path.join(path_to_data, batch_dir, file_path)

        # batch1 has extra 'PAX6_'
        if batch_dir == '20191021-original':
            dir_name = dir_name.replace("PAX6_", "")

        # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
        new_name = "%s/%s" % (dir_name, img_name)

        dataset_name = "%s-%s" % (gene, stage)
        target = "%sDataset:name:%s" % (project_name, dataset_name)
        tsv_writer.writerow([target, image_path, new_name])
