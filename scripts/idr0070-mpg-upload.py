
#!/usr/bin/env python

# This has to run as user omero-server.
# Assumes that omero-upload was installed on the server.

# sudo su omero-server
# . /opt/omero/server/venv3/bin/activate
# python idr0070-mpg-upload.py

import csv
import os
import omero.clients
import omero.cli
from omero.model import FileAnnotationI
from omero_upload import upload_ln_s

"""
This script uploads the mpg files found in
'idr0070-experimentA-filePaths.tsv' since these are not
supported by Bio-Formats for regular import.

They are uploaded 'in-place' and attached to the appropriate
Dataset instead of being imported into it.
"""

project_name = 'idr0070-kerwin-hdbr/experimentA'

OMERO_DATA_DIR = '/data/OMERO'
NAMESPACE = 'openmicroscopy.org/idr/analysis/original'
MIMETYPE = 'video/mpeg'


def upload_and_link(conn, target, attachment):
    print("upload_and_link", attachment)
    fo = upload_ln_s(conn.c, attachment, OMERO_DATA_DIR, MIMETYPE)
    fa = FileAnnotationI()
    fa.setFile(fo._obj)
    fa.setNs(omero.rtypes.rstring(NAMESPACE))
    fa = conn.getUpdateService().saveAndReturnObject(fa)
    fa = omero.gateway.FileAnnotationWrapper(conn, fa)
    target.linkAnnotation(fa)


def has_file_annotation(target, path):
    for ann in target.listAnnotations():
        if hasattr(ann, 'file'):
            orig_file = target._conn.getObject('OriginalFile', ann.file.id)
            if (orig_file.path + '/' + orig_file.name) == path:
                return True
    return False


def main(conn):

    project = conn.getObject("Project", attributes={'name': project_name})
    print("Project", project.id)

    datasets_by_name = {}
    for dataset in project.listChildren():
        datasets_by_name[dataset.name] = dataset

    with open('idr0070-experimentA-filePaths.tsv', mode='r') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        for row in tsv_reader:
            mpg_path = row[1]
            mpg_name = row[2]
            if not mpg_path.endswith(".mpg"):
                continue

            project_dataset = row[0]
            # Project:name:idr0070-kerwin-hdbr/experimentA/Dataset:name:GAP43-CS17
            dataset_name = project_dataset.split('/Dataset:name:')[1]
            if dataset_name not in datasets_by_name:
                print("No Dataset Found", dataset_name)
                continue
            
            dataset = datasets_by_name[dataset_name]
            # IF previously linked to Dataset, remove
            to_delete = list(dataset.listAnnotations(ns=NAMESPACE))
            if len(to_delete) > 0:
                print("Deleting from ", dataset_name)
                for ann in to_delete:
                    conn.deleteObjects('Annotation', [ann.id])

            if not os.path.exists(mpg_path):
                print("FILE NOT FOUND", mpg_path)
                continue

            # Find image with correct name in Dataset
            jpg_name = mpg_name.replace('.mpg', '.jpg')
            images = conn.getObjects(
                "Image",
                attributes={'name': jpg_name},
                opts={'dataset': dataset.id}
            )
            images = list(images)
            if len(images) == 0:
                # Somehow 'HDBR_FGFR3_CS23_ISH/3Dview.jpg' is never found
                # HDBR_FGFR3_CS23_ISH/3Dview.jpg name never matches - hard-code...
                img = conn.getObject("Image", 9838638)
                print("Found HDBR_FGFR3_CS23_ISH/3Dview.jpg", img)
                images = [img]
            if len(images) == 0:
                print("Found NO jpg named", jpg_name, 'in', dataset_name, dataset.id)
            elif len(images) > 1:
                print("Found multiple jpgs for", jpg_name, 'in', dataset_name)
            else:
                image = images[0]
                if not has_file_annotation(image, mpg_path):
                    upload_and_link(conn, image, mpg_path)
                else:
                    print(image.name, "already has", mpg_path)


if __name__ == '__main__':
    with omero.cli.cli_login() as c:
        conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
        main(conn)
