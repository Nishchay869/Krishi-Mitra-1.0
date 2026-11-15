"""Merge several downloaded leaf-disease datasets into one Crop___Disease folder tree.

Each source is a folder that somewhere below it contains class folders full of images
(nested train/ valid/ test/ splits are fine; same-named classes are merged). Give a crop
name for single-crop datasets whose folders are only disease names:

  python scripts/merge_disease_datasets.py data/disease_merged \\
      data/raw/plantvillage \\
      data/raw/paddy_doctor/train_images:Rice \\
      data/raw/cassava_by_class:Cassava \\
      --map data/raw/class_map.json --min-images 50

Class folder names become Crop___Disease:
  - "Tomato___Late_blight" stays as is (PlantVillage style);
  - "brown_spot" with crop Rice becomes "Rice___brown_spot";
  - "Healthy", "normal" become "healthy";
  - folders without "___" and without a crop are skipped and listed.

--map is an optional JSON object renaming final class names, e.g. to unify spellings
across datasets: {"Rice___Brown_Spot": "Rice___brown_spot", "Rice___bacterial_leaf_blight": null}
(null drops the class). Exact duplicate images are skipped. Files are copied unless
--link is given (symlinks: saves disk, but keep the raw folders).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp'}
HEALTHY_WORDS = {'healthy', 'normal', 'fresh', 'healthy_leaf', 'healthy_leaves'}
SPLIT_DIRS = {'train', 'training', 'valid', 'validation', 'val', 'test', 'testing', 'images'}


def clean(text):
    text = re.sub(r'\s+', '_', text.strip())
    return re.sub(r'[^\w(),.-]', '', text)


def class_name(folder_name, crop):
    if '___' in folder_name:
        plant, disease = folder_name.split('___', 1)
    elif crop:
        plant, disease = crop, folder_name
    else:
        return None
    plant, disease = clean(plant), clean(disease)
    if disease.lower() in HEALTHY_WORDS:
        disease = 'healthy'
    if not plant or not disease:
        return None
    return f'{plant}___{disease}'


def class_dirs(root):
    """Folders that directly contain images, excluding bare split folders like train/."""
    for dirpath, _, files in os.walk(root):
        d = Path(dirpath)
        if any(Path(f).suffix.lower() in IMAGE_EXTS for f in files) and d.name.lower() not in SPLIT_DIRS:
            yield d


def file_hash(path):
    h = hashlib.sha1()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('output', help='destination folder (must be empty or not exist)')
    p.add_argument('sources', nargs='+', help='PATH or PATH:Crop')
    p.add_argument('--map', action='append', help='JSON file renaming/dropping classes (repeatable)')
    p.add_argument('--min-images', type=int, default=30, help='drop classes with fewer images')
    p.add_argument('--max-per-class', type=int, default=0, help='cap images per class (0 = no cap)')
    p.add_argument('--link', action='store_true', help='symlink instead of copy')
    p.add_argument('--dry-run', action='store_true', help='only print the class summary')
    a = p.parse_args()

    out = Path(a.output)
    if out.exists() and any(out.iterdir()) and not a.dry_run:
        sys.exit(f'{out} is not empty; choose a new folder so old and new data do not mix.')
    mapping = {}
    for map_file in a.map or []:
        for key, value in json.loads(Path(map_file).read_text()).items():
            if '___' not in key:  # raw folder names are matched case/space-insensitively
                key = ' '.join(key.lower().replace('_', ' ').split())
            mapping[key] = value

    plan, skipped = defaultdict(list), set()
    for spec in a.sources:
        path, _, crop = spec.partition(':') if not Path(spec).exists() else (spec, '', '')
        root = Path(path)
        if not root.is_dir():
            sys.exit(f'Source not found: {root}')
        for d in class_dirs(root):
            raw = ' '.join(d.name.lower().replace('_', ' ').split())
            if raw in mapping:  # map keys may also be raw folder names, e.g. PlantDoc's "tomato leaf late blight"
                name = mapping[raw]
            else:
                name = class_name(d.name, crop)
                if name is None:
                    skipped.add(f'{root}/{d.relative_to(root)}')
                    continue
                name = mapping.get(name, name)
            if name is None:
                continue
            plan[name].extend(f for f in sorted(d.iterdir()) if f.suffix.lower() in IMAGE_EXTS)

    if skipped:
        print('Skipped folders (no "___" and no crop given; add :Crop to the source):')
        for s in sorted(skipped):
            print(f'  {s}')

    seen, counts, dupes = set(), Counter(), 0
    for name in sorted(plan):
        files = plan[name]
        if len(files) < a.min_images:
            print(f'Dropping {name}: only {len(files)} images (< --min-images {a.min_images})')
            continue
        if a.max_per_class:
            files = files[:a.max_per_class]
        if a.dry_run:
            counts[name] = len(files)
            continue
        dest = out / name
        dest.mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(files):
            digest = file_hash(f)
            if digest in seen:
                dupes += 1
                continue
            seen.add(digest)
            target = dest / f'{i:06d}{f.suffix.lower()}'
            if a.link:
                target.symlink_to(f.resolve())
            else:
                shutil.copy2(f, target)
            counts[name] += 1

    print(f'\n{len(counts)} classes, {sum(counts.values())} images'
          + (f', {dupes} duplicate images skipped' if dupes else ''))
    crops = Counter(n.split('___')[0] for n in counts)
    print('Crops: ' + ', '.join(f'{c} ({k} classes)' for c, k in sorted(crops.items())))
    if counts:
        small = min(counts.values())
        large = max(counts.values())
        print(f'Images per class: min {small}, max {large}')
        if large > 10 * small:
            print('Classes are very unbalanced; consider --max-per-class (training also uses class weights).')
    if not a.dry_run:
        (out.parent / f'{out.name}_class_counts.json').write_text(json.dumps(dict(sorted(counts.items())), indent=2))


if __name__ == '__main__':
    main()
