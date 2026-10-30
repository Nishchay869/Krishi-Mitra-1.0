"""Import reviewed YOLO lesion annotations from any licensed dataset via JSONL."""
import argparse
import json
import shutil
from pathlib import Path

from .common import read_manifest, sha256


def validate_label(text, task, num_classes):
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        cls = int(fields[0])
        values = [float(v) for v in fields[1:]]
        if not 0 <= cls < num_classes or not all(0 <= v <= 1 for v in values):
            raise ValueError('Invalid class or normalized coordinates')
        if task == 'detect':
            if len(values) != 4 or values[2] <= 0 or values[3] <= 0:
                raise ValueError('Detection requires class xc yc width height')
            x, y, w, h = values
            if x-w/2 < -1e-6 or y-h/2 < -1e-6 or x+w/2 > 1+1e-6 or y+h/2 > 1+1e-6:
                raise ValueError('Bounding box extends outside image')
        elif len(values) < 6 or len(values) % 2:
            raise ValueError('Segmentation requires at least three polygon vertices')


def prepare(manifest, destination, names, task):
    from PIL import Image
    import yaml
    rows = read_manifest(manifest)
    dest = Path(destination).resolve()
    if dest.exists():
        raise ValueError('Choose a new destination; imports never overwrite data')
    groups, hashes = {}, {}
    checked = []
    for row in rows:
        split = row['split']
        for table, key in ((groups, row['group']), (hashes, sha256(row['image']))):
            if key in table and table[key] != split:
                raise ValueError(f'Train/evaluation leakage: {row["image"]}')
            table[key] = split
        with Image.open(row['image']) as image:
            if image.getexif().get(274, 1) != 1:
                raise ValueError('Normalize EXIF orientation BEFORE annotation')
            image.load()
        # Whole-leaf bounding boxes / image-level class labels are not lesion annotations.
        if row['kind'] == 'leaf' and row.get('annotation_scope') != 'lesion_reviewed':
            raise ValueError('Leaf images require reviewed lesion annotations, including healthy empty labels')
        text = Path(row['label']).read_text() if row.get('label') else ''
        if row['kind'] == 'leaf' and not row.get('label'):
            raise ValueError('Leaf image needs explicit label file (empty only after healthy review)')
        if row['kind'] == 'background' and text.strip():
            raise ValueError('Negative image must have empty detector annotations')
        validate_label(text, task, len(names))
        checked.append((row, text))
    # Validate everything before creating the output dataset.
    for index, (row, text) in enumerate(checked):
        split = row['split']
        stem = f'{index:07d}_{sha256(row["image"])[:12]}'
        image_dir, label_dir = dest/'images'/split, dest/'labels'/split
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(row['image']) as image:
            image.convert('RGB').save(image_dir/f'{stem}.png')
        (label_dir/f'{stem}.txt').write_text(text)
        gate_dir = dest/'gate'/split/row['kind']
        gate_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_dir/f'{stem}.png', gate_dir/f'{stem}.png')
    (dest/'dataset.yaml').write_text(yaml.safe_dump({
        'path': str(dest), 'train': 'images/train', 'val': 'images/val',
        'test': 'images/test', 'names': dict(enumerate(names))}))
    (dest/'provenance.json').write_text(json.dumps(rows, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest'); parser.add_argument('destination')
    parser.add_argument('--names', nargs='+', required=True)
    parser.add_argument('--task', choices=['detect', 'segment'], default='segment')
    args = parser.parse_args()
    prepare(args.manifest, args.destination, args.names, args.task)
