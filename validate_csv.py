import csv
import os

gene = "PAX6"
project = "Project:name:idr0070-kerwin-hdbr/experimentA/"
path_to_data = "/uod/idr/filesets/idr0070-kerwin-hdbr/20191021-original/HDBR_PAX6"
# path_to_data = "/Users/willadmin/Desktop/IDR/idr0070/data/HDBR_PAX6"

found = []
not_found = []
print("Reading CSV...")
with open('HDBR_PAX6.csv', mode='r') as csv_file:
    # csv_reader = csv.DictReader(csv_file)
    csv_reader = csv.reader(csv_file)
    line_count = 0

    for row in csv_reader:

        # ignore first row of CSV (column names)
        if line_count == 0:
            # print('Column names...')
            # print(row)
            line_count += 1
            continue

        # Read the columns we need...
        dir_name = row[0].replace("PAX6_", "")
        img_name = row[1]

        image_path = "%s/%s/%s" % (path_to_data, dir_name, img_name)

        # e.g. CS15_IHC_transverse/CS15_N733_64.jpg
        new_name = "%s/%s" % (dir_name, img_name)

        # check we're creating correct paths
        if not os.path.exists(image_path):
            print(new_name)
            not_found.append(image_path)
            continue
        found.append(image_path)

        # TODO - check for img_name.replace('.jpg', '_mapped.png')
        mapped_png_path = image_path.replace(".jpg", "_mapped.png")
        if os.path.exists(mapped_png_path):
            line_count += 1
            found.append(mapped_png_path)

        line_count += 1
    print("Not found on disk: ", len(not_found))

found_lowercase = [f.lower() for f in found]

print("\nReading images on disk...")
# iterate all images to find which are not listed above...
not_found = []
for root, dirs, files in os.walk(path_to_data):
    archive_root = os.path.relpath(root, path_to_data)
    for f in files:
        fullpath = os.path.join(root, f)
        if fullpath not in found and (f.endswith('.png') or f.endswith('.jpg')):
            print(fullpath.replace(path_to_data, ""))
            not_found.append(fullpath)
            # Check if it's only a case-sensitive mismatch:
            if fullpath.lower() in found_lowercase:
                idx = found_lowercase.index(fullpath.lower())
                print('CASE mismatch! In CSV:', found[idx].replace(path_to_data, ""))

print("Not found in CSV: ", len(not_found))
