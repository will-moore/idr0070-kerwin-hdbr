import csv
import os
import glob

"""
This script uses csv files for each of the batch of files uploaded.
It combines them into a single 'idr0070-experimentA-annotation.csv'
suitable for creating bulk annotations in IDR.

It also handles the multiple images in Multi-Image-Filesets,
creating additional rows in the annotation.csv.
E.g. for image1.scn in the input csv, we have imported images:
image1.scn [macro], image1.scn [1], image1.scn [2].

We get the list of ALL imported images as 'imported_image_names.csv'

Usage: run from the idr0070-kerwin-hdbr root dir:
$ python scripts/csv_to_annotations_csv.py
"""


# We process '20191021-original' first since it has the columns
# we want.
batch_dirs = [
    '20191021-original', '20200214-ftp', '20200414-Batch3-ftp',
    '20200422-Batch5', '20200417-Batch4', '20200423-Batch6'
]

# Read the csv file from each batch, adding to single list of rows.
csv_rows = []
col_names = None
for dir_name in batch_dirs:
    # Find csv file in each dir...
    path_to_csv = os.path.join(os.getcwd(), 'experimentA', dir_name)
    csv_files = glob.glob(os.path.join(path_to_csv, "*.csv"))
    assert len(csv_files) == 1
    print('csv_files', path_to_csv, csv_files)

    with open(csv_files[0], mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)
        # Need to know dir_name below...
        cols = list(rows[0].keys())
        if col_names is None:
            col_names = cols
        for r in rows:
            # print(r)
            assert r['Dataset Name'] is not None
            assert r["Image Name"] is not None
            assert r["Characteristics [Developmental Stage]"]
            assert r['Comment [Gene Symbol]']
            assert r['Comment [Image File Path]']
            r['batch_dir'] = dir_name
            # Only batch 1 has 'Antibody Identifier'
            if 'Antibody Identifier' not in r:
                r['Antibody Identifier'] = r.get('Term Source 2 Accession')
        # Ignore first row (column names)
        csv_rows.extend(rows)
        print(dir_name, len(rows), 'rows')

# if we have imported images and used validate_imports.py to generate imported_image_names.csv
imported_image_names = None
if os.path.exists('imported_image_names.csv'):
    with open('imported_image_names.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        imported_image_names = [r[0] for r in csv_reader]

unique_names = []
def write_row(writer, csv_row):
    if csv_row[1] not in unique_names:
        writer.writerow(csv_row)
        unique_names.append(csv_row[1])
    else:
        print('duplicate', csv_row[1])

mpg_count = 0
# We create the bulk metadata .csv
with open('idr0070-experimentA-annotation.csv', mode='w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(col_names)

    for row in csv_rows:
        # Read the columns we need...
        dir_name = row['Dataset Name']
        img_name = row["Image Name"]
        stage = row["Characteristics [Developmental Stage]"]
        gene = row['Comment [Gene Symbol]']
        file_path = row['Comment [Image File Path]']

        batch_dir = row['batch_dir']

        # batch1 has extra 'PAX6_'
        if batch_dir == '20191021-original':
            dir_name = dir_name.replace("PAX6_", "")

        # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
        new_name = "%s/%s" % (dir_name, img_name)
        dataset = "%s-%s" % (gene, stage)

        # Once we have imported images and used validate_imports.py to generate
        # imported_image_names.csv
        if imported_image_names:
            # convert from dict to list
            csv_row = [row.get(name, '') for name in col_names]
            csv_row[0] = dataset
            # We can use those names to find additional images in series...
            # e.g. name [0], name [macro], name [macro image], name [label image]
            # and duplicate rows in the annotation.csv
            has_series = False

            macros = ['macro', 'macro image', 'label image', '0']
            for macro in macros:
                if f'{ new_name } [{ macro }]' in imported_image_names:
                    has_series = True
                    csv_row[1] = f'{ new_name } [{ macro }]'
                    write_row(csv_writer, csv_row)
            
            series_id = 1
            while f'{ new_name } [{ series_id }]' in imported_image_names:
                csv_row[1] = f'{ new_name } [{ series_id }]'
                write_row(csv_writer, csv_row)
                series_id += 1

            if not has_series:
                # e.g. jpgs etc don't have series
                csv_row[1] = new_name
                if new_name not in imported_image_names:   # and not new_name.endswith('.mpg'):
                    mpg_count += 1
                    print('Not imported', mpg_count, new_name)
                else:
                    write_row(csv_writer, csv_row)

# Check for any imported images without rows in annotations.csv
for name in imported_image_names:
    if name not in unique_names:
        print("NO csv annotations for ", name)