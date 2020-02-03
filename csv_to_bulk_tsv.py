import csv
import os

gene = "PAX6"
project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr/20191021-original/HDBR_PAX6"
# path_to_data = "/Users/willadmin/Desktop/IDR/idr0070/data/HDBR_PAX6"

with open('HDBR_PAX6.csv', mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0

    with open('idr0070-experimentA-filePaths.tsv', mode='w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')

        for row in csv_reader:

            # ignore first row of CSV (column names)
            if line_count == 0:
                line_count += 1
                continue

            # Read the columns we need...
            dir_name = row[0].replace("PAX6_", "")
            img_name = row[1]
            stage = row[7]

            image_path = "%s/%s/%s" % (path_to_data, dir_name, img_name)

            # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
            new_name = "%s/%s" % (dir_name, img_name)

            # check we're creating correct paths
            if not os.path.exists(image_path):
                print(new_name)
                continue

            target = "%sDataset:name:%s-%s" % (project, gene, stage)
            tsv_writer.writerow([target, image_path, new_name])

            line_count += 1
