import csv
import os

gene = "PAX6"
project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr/20191021-original/HDBR_PAX6"
# path_to_data = "/Users/willadmin/Desktop/IDR/idr0070/data/HDBR_PAX6"

with open('HDBR_PAX6.csv', mode='r') as csv_file:
    # csv_reader = csv.DictReader(csv_file)
    csv_reader = csv.reader(csv_file)
    line_count = 0

    with open('idr0070-experimentA-filePaths.tsv', mode='w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        # tsv_writer.writerow(['John Smith', 'Accounting', 'November'])
        # tsv_writer.writerow(['Erica Meyers', 'IT', 'March'])

        for row in csv_reader:
            if line_count == 0:
                print('Column names...')
                print(row)
                line_count += 1
                continue

            stage_idx = 7
            dir_idx = 0
            img_idx = 1

            stage = row[stage_idx]
            target = "%sDataset:name:%s-%s" % (project, gene, stage)

            dir_name = row[dir_idx].replace("PAX6_", "")
            img_name = row[img_idx]
            image_path = "%s/%s/%s" % (path_to_data, dir_name, img_name)

            # CS15_IHC_transverse/CS15_N733_64.jpg
            new_name = "%s/%s" % (dir_name, img_name)

            # check we're creating correct paths
            if not os.path.exists(image_path):
                print('NOT FOUND: %s' % image_path)
                break
            tsv_writer.writerow([target, image_path, new_name])

            # TODO - check for img_name.replace('.jpg', '_mapped.png')
            mapped_png = image_path.replace(".jpg", "_mapped.png")
            if os.path.exists(mapped_png):
                new_name = "mapped_%s" % new_name
                tsv_writer.writerow([target, mapped_png, new_name])

            line_count += 1

        print('Processed %s lines.' % line_count)
