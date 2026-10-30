"""Stage locally downloaded field datasets for lesion annotation; never invent labels."""
import argparse
import csv
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source', choices=['plantdoc','fieldplant','cassava','fgvc'])
    p.add_argument('images'); p.add_argument('output')
    p.add_argument('--metadata', help='Optional Cassava/FGVC CSV containing image_id and label')
    a=p.parse_args(); labels={}
    if a.metadata:
        with open(a.metadata, newline='') as handle:
            for row in csv.DictReader(handle):
                labels[row['image_id']] = row['label']
    rows=[]
    for path in sorted(Path(a.images).resolve().rglob('*')):
        if path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):
            continue
        rows.append({'image':str(path),'source':a.source,'domain':'field','kind':'leaf',
                     'group':'REQUIRED_FARM_PLANT_CAPTURE_GROUP','split':'REQUIRED_GROUP_SPLIT',
                     'annotation_scope':'needs_lesion_annotation','label':None,
                     'original_image_class':labels.get(path.name)})
    if not rows:
        raise ValueError('No images found')
    with open(a.output, 'x') as handle:
        handle.write(''.join(json.dumps(r)+'\n' for r in rows))
    print('Staging only. Assign capture groups and held-out splits, then annotate lesions before import.')


if __name__ == '__main__': main()
