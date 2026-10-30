"""Background replacement preserves leaf coordinates and reviewed lesion labels."""
import argparse
import json
import random
from pathlib import Path

from .common import read_manifest, sha256


def synthesize(manifest, backgrounds, output, copies, seed):
    from PIL import Image, ImageOps
    import numpy as np
    from rembg import remove, new_session
    rows = read_manifest(manifest)
    bank = [p for p in Path(backgrounds).rglob('*') if p.suffix.lower() in ('.jpg', '.jpeg', '.png')]
    # Count distinct content, not copies of one background.
    bank = list({sha256(p): p for p in bank}.values())
    if len(bank) < 2000:
        raise ValueError('Provide at least 2,000 distinct, licensed training-only backgrounds')
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    rng, session, generated = random.Random(seed), new_session('u2net'), []
    for index, row in enumerate(rows):
        if row['split'] != 'train' or row['kind'] != 'leaf':
            continue
        if row.get('annotation_scope') != 'lesion_reviewed' or not row.get('label'):
            raise ValueError('Do not convert image-level labels into fabricated lesion annotations')
        with Image.open(row['image']) as original:
            if original.getexif().get(274, 1) != 1:
                raise ValueError('Normalize EXIF before annotation')
            leaf = original.convert('RGB')
        mask = remove(leaf, session=session, only_mask=True).convert('L')
        ratio = float((np.asarray(mask) > 127).mean())
        if not .05 < ratio < .95:
            continue  # Bad extraction goes to human review, never silently accepted.
        for version in range(copies):
            background = rng.choice(bank)
            with Image.open(background) as image:
                field = ImageOps.fit(image.convert('RGB'), leaf.size)
            stem = f'{index:07d}_{version}'
            Image.composite(leaf, field, mask).save(out/f'{stem}.jpg', quality=95)
            mask.save(out/f'{stem}.mask.png')
            (out/f'{stem}.txt').write_text(Path(row['label']).read_text())
            generated.append({**row, 'image': str(out/f'{stem}.jpg'),
                              'label': str(out/f'{stem}.txt'), 'source': 'synthetic',
                              'background_sha256': sha256(background),
                              'annotation_scope': 'needs_mask_review'})
    (out/'review.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in generated))
    print('Review every composite and mask; change annotation_scope to lesion_reviewed only after approval.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('backgrounds'); p.add_argument('output')
    p.add_argument('--copies', type=int, default=3); p.add_argument('--seed', type=int, default=42)
    a = p.parse_args(); synthesize(a.manifest, a.backgrounds, a.output, a.copies, a.seed)
