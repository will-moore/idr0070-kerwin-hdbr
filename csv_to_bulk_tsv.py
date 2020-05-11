import csv
import os
import glob

project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr/"
# path_to_data = "/Users/wmoore/Desktop/IDR/idr0070/20191021-original/HDBR_PAX6"

batch_dirs = [
    '20191021-original', '20200414-Batch3-ftp', '20200422-Batch5',
    '20200214-ftp', '20200417-Batch4', '20200423-Batch6'
]

# Read the csv file from each batch, adding to single list of rows.
csv_rows = []
for dir_name in batch_dirs:
    # Find csv file in each dir...
    path_to_csv = os.path.join(os.getcwd(), dir_name)
    csv_files = glob.glob(os.path.join(path_to_csv, "*.csv"))
    assert len(csv_files) == 1
    print('csv_files', path_to_csv, csv_files)

    with open('idr0070-experimentA-annotation.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
        # Need to know dir_name below...
        for r in rows:
            r['batch_dir'] = dir_name
        # Ignore first row (column names)
        csv_rows.extend(rows[1:])
        print(dir_name, len(rows), 'rows')


# We create the bulk import .tsv and the bulk metadata .csv at the same time...
with open('idr0070-experimentA-annotation.csv', mode='w') as csv_file:
    csv_writer = csv.writer(csv_file)

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
            image_path = "%s/%s/%s" % (path_to_data, batch_dir, file_path)

            # batch1 has extra 'PAX6_'
            if batch_dir == '20191021-original':
                dir_name = dir_name.replace("PAX6_", "")

            # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
            new_name = "%s/%s" % (dir_name, img_name)

            # check we're creating correct paths
            if not os.path.exists(image_path):
                print("Not found:", image_path)
                continue

            dataset = "%s-%s" % (gene, stage)
            target = "%sDataset:name:%s" % (project, dataset)
            tsv_writer.writerow([target, image_path, new_name])

            # Edit rows and write to new csv
            row[0] = dataset
            row[1] = new_name
            csv_writer.writerow(row)

            line_count += 1
