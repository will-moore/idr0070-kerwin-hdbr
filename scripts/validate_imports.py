
import requests
import csv
import os

"""
This script is used to check all the imported images against the 
bulk import filePaths.tsv to check if any failed to import.

Failed imports are listed in a 'reimport.tsv' which can be used
for re-importing just those files.

It also generates a list of 'imported_image_names.csv' that is
required by the 'csv_to_annotations_csv.py` script to know
which imports resulted in Multi-Image-Filesets.

We use the public webclient API (no login needed) which means we
don't need ports available for OMERO API access.
"""

test_server = "http://example.openmicroscopy.org"
project_id = 1109
datasets_url = f'{test_server}/webclient/api/datasets/?id={project_id}'

datasets = requests.get(datasets_url).json()['datasets']
total_images = 0
fs_images = 0
total_filesets = 0

if not os.path.exists('imported_image_names.csv'):

    with open('imported_image_names.csv', mode='w') as csv_file:
        csv_writer = csv.writer(csv_file)

        for d in datasets:
            # load images
            print("Dataset", d['id'], d['name'])
            dataset_id = d['id']
            img_url = f'{test_server}/webclient/api/images/?id={dataset_id}'
            images = requests.get(img_url).json()['images']
            filesets = {}
            total_images += len(images)
            for i in images:
                if i['filesetId'] not in filesets:
                    filesets[i['filesetId']] = []
                filesets[i['filesetId']].append(i)
                csv_writer.writerow([i['name']])
            total_filesets += len(filesets)
            for fs_imgs in filesets.values():
                imgs = [i for i in fs_imgs if "[macro" not in i['name']]
                if len(imgs) > 1:
                    print([i['name'] for i in imgs])
                    fs_images += len(imgs)

            print('total_filesets', total_filesets)
            print('total_images', total_images)
            print('fs_images', fs_images)

print("------------ comparing imported against idr0070-experimentA-filePaths.tsv ----------------")
not_imorted_count = 0
to_reimport = []
with open('imported_image_names.csv', mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    imported_images = [r[0] for r in csv_reader]

    with open('idr0070-experimentA-filePaths.tsv', mode='r') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        # Find any imported image that matches
        for row in tsv_reader:
            image_name = row[2]
            if image_name.endswith(".mpg"):
                continue
            imported = False
            # print('check', image_name)
            for i in imported_images:
                # print(i, image_name in i)
                if image_name in i:
                    imported = True
                    break
            if not imported:
                print("NOT imported: ", image_name)
                not_imorted_count += 1
                print("not_imorted_count", not_imorted_count)
                to_reimport.append(row)

with open('reimport.tsv', mode='w') as tsv_file:
    tsv_writer = csv.writer(tsv_file, delimiter='\t')
    tsv_writer.writerows(to_reimport)


