import csv
import os

gene = "PAX6"
project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr/20191021-original/HDBR_PAX6"
# path_to_data = "/Users/willadmin/Desktop/IDR/idr0070/data/HDBR_PAX6"

line_count = 0
with open('idr0070-experimentA-filePaths.tsv', mode='w') as tsv_file:
    tsv_writer = csv.writer(tsv_file, delimiter='\t')

    for root, dirs, files in os.walk(path_to_data):
        archive_root = os.path.relpath(root, path_to_data)
        for f in files:
            image_path = os.path.join(root, f)
            if f.endswith('.png') or f.endswith('.jpg'):

                dirname = os.path.basename(root)
                stage = dirname.split('_')[0]

                target = "%sDataset:name:%s-%s" % (project, gene, stage)

                new_name = f
                if new_name.endswith("_mapped.png"):
                    # remove _mapped from end and prepend it instead
                    new_name = new_name.replace("_mapped", "")
                    new_name = "mapped_%s" % new_name
                new_name = "%s/%s" % (dirname, new_name)

                tsv_writer.writerow([target, image_path, new_name])
                line_count += 1

print("wrote %s lines" % line_count)
