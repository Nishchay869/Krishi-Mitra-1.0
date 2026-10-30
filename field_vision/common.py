import hashlib
import json
from pathlib import Path

FALLBACK = ('Uncertain diagnosis. Please capture the leaf closer, in indirect daylight, '
            'and steady the camera.')


def read_manifest(path):
    path = Path(path).resolve()
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        for key in ('image', 'split', 'group', 'source', 'kind'):
            if not row.get(key):
                raise ValueError(f'Line {number}: missing {key}')
        if row['split'] not in ('train', 'val', 'test') or row['kind'] not in ('leaf', 'background'):
            raise ValueError(f'Line {number}: invalid split or kind')
        for key in ('image', 'label'):
            if row.get(key):
                row[key] = str((path.parent / row[key]).resolve())
                if not Path(row[key]).is_file():
                    raise ValueError(f'Missing file: {row[key]}')
        rows.append(row)
    if not rows:
        raise ValueError('Empty manifest')
    return rows


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def wilson(successes, total, z=1.96):
    if not total:
        return (0., 1.)
    p = successes / total
    denom = 1 + z*z / total
    center = (p + z*z / (2*total)) / denom
    radius = z * ((p*(1-p)/total + z*z/(4*total*total)) ** .5) / denom
    return max(0., center-radius), min(1., center+radius)
