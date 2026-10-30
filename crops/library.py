"""Bundled crop reference. No runtime AI or external API calls.

Ranges are ecological or regional reference values, not irrigation doses.
Intercrops, rotations, habitat strips and bed layouts are explicitly distinguished.
"""
import json
from functools import lru_cache
from pathlib import Path
from django.utils.text import slugify
from accounts.onboarding import CROP_GROUPS

@lru_cache(maxsize=1)
def catalog():
    records = json.loads((Path(__file__).parent / 'data/library.json').read_text())
    result = []
    for group, crops in CROP_GROUPS:
        for name, photo in crops:
            result.append(dict(records[name], name=name, photo=photo,
                               slug=slugify(name), group=group, group_slug=slugify(group)))
    return result
