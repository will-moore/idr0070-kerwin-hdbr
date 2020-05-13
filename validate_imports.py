
# import argparse
# import sys

# import omero.clients
# from omero.cli import cli_login
# from omero.gateway import BlitzGateway

# def main(argv):
#     parser = argparse.ArgumentParser()
#     parser.add_argument('project_id', type=int)
#     args = parser.parse_args(argv)

#     with cli_login() as cli:
#         conn = BlitzGateway(client_obj=cli._client)
#         project = conn.getObject("Project", args.project_id)

#         for dataset in project.listChildren():
#             print("Dataset: ", dataset.name)
#             images = list(dataset.listChildren())
#             # Find filesets with 2 or more images:
#             filesets = {}
#             for i in images:
#                 if i.fileset.id not in filesets:
#                     filesets[i.fileset.id] = []
#                 filesets[i.fileset.id].append(i)
#             for imgs in filesets.values():
#                 if len(imgs) > 2:
#                     print([i.name for i in imgs])

# if __name__ == '__main__':
#     main(sys.argv[1:])

import requests
import csv
import os

url = "http://ome-idr-covid-1.openmicroscopy.org/webclient/api/datasets/?id=1109"

datasets = requests.get(url).json()['datasets']
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
            img_url = f'http://ome-idr-covid-1.openmicroscopy.org/webclient/api/images/?id={dataset_id}'
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


