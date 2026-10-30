"""Materialize training-only augmentations with synchronized instance masks."""
import argparse
import shutil
from pathlib import Path


def pipeline(size=1024, seed=42):
    import albumentations as A
    import cv2
    return A.Compose([
        A.LongestMaxSize(max_size=size),
        A.PadIfNeeded(min_height=size, min_width=size, border_mode=cv2.BORDER_CONSTANT, fill=114, fill_mask=0),
        A.ShiftScaleRotate(shift_limit=.08, scale_limit=.15, rotate_limit=25,
                          border_mode=cv2.BORDER_CONSTANT, fill=114, fill_mask=0, p=.65),
        A.RandomSunFlare(flare_roi=(0, 0, 1, .6), src_radius=max(20, size//8), p=.15),
        A.RandomShadow(p=.3),
        A.ColorJitter(brightness=.35, contrast=.3, saturation=.25, hue=.04, p=.65),
        A.OneOf([A.MotionBlur(blur_limit=(3, 7)), A.GaussianBlur(blur_limit=(3, 5)),
                 A.ISONoise(), A.GaussNoise(std_range=(.01, .06))], p=.4),
        A.CoarseDropout(num_holes_range=(1, 5), hole_height_range=(.03, .14),
                        hole_width_range=(.03, .14), fill=114, fill_mask=0, p=.35),
        A.HorizontalFlip(p=.5),
    ], seed=seed)


def augment(source, destination, task, copies, size, seed):
    import cv2
    import numpy as np
    import yaml
    source, dest = Path(source).resolve(), Path(destination).resolve()
    if dest == source or source in dest.parents:
        raise ValueError('Destination must be outside the source dataset')
    shutil.copytree(source, dest)  # Refuse to overwrite an existing dataset.
    transform = pipeline(size, seed)
    for image_path in sorted((source/'images/train').glob('*')):
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f'Cannot decode {image_path}')
        h, w = image.shape[:2]
        rows = (source/'labels/train'/f'{image_path.stem}.txt').read_text().splitlines()
        masks, classes = [], []
        for row in rows:
            if not row.strip():
                continue
            fields = row.split(); cls, xy = int(fields[0]), np.array(fields[1:], dtype=float)
            if task == 'detect':
                x, y, bw, bh = xy
                xy = np.array([x-bw/2, y-bh/2, x+bw/2, y-bh/2, x+bw/2, y+bh/2, x-bw/2, y+bh/2])
            points = np.rint(xy.reshape(-1, 2)*[w, h]).astype(np.int32)
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [points], 1)
            masks.append(mask); classes.append(cls)
        for version in range(copies):
            result = transform(image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB), masks=masks)
            lines = []
            for cls, mask in zip(classes, result['masks']):
                if np.count_nonzero(mask) < 8:
                    continue
                if task == 'detect':
                    ys, xs = np.where(mask > 0)
                    x1, x2, y1, y2 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
                    values = [(x1+x2)/(2*size), (y1+y2)/(2*size), (x2-x1)/size, (y2-y1)/size]
                    lines.append(str(cls)+' '+' '.join(f'{v:.6f}' for v in values))
                else:
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) < 4 or len(contour) < 3:
                            continue
                        values = contour.reshape(-1).astype(float)/size
                        lines.append(str(cls)+' '+' '.join(f'{v:.6f}' for v in values))
            stem = f'{image_path.stem}_aug{version}'
            cv2.imwrite(str(dest/'images/train'/f'{stem}.jpg'), cv2.cvtColor(result['image'], cv2.COLOR_RGB2BGR))
            (dest/'labels/train'/f'{stem}.txt').write_text('\n'.join(lines))
    cfg = yaml.safe_load((dest/'dataset.yaml').read_text()); cfg['path'] = str(dest)
    (dest/'dataset.yaml').write_text(yaml.safe_dump(cfg))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('destination')
    p.add_argument('--task', choices=['detect', 'segment'], default='segment')
    p.add_argument('--copies', type=int, default=2); p.add_argument('--size', type=int, default=1024)
    p.add_argument('--seed', type=int, default=42)
    a = p.parse_args(); augment(a.source, a.destination, a.task, a.copies, a.size, a.seed)
