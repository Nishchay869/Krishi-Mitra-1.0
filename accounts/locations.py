"""Bundled state/district choices shared with the mandi location catalog."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def state_districts():
    catalog = json.loads((Path(__file__).resolve().parent.parent / 'market/data/catalog.json').read_text())
    return {state['name']: sorted({d['name'] for d in catalog['districts'] if d['state'] == state['id']})
            for state in sorted(catalog['states'], key=lambda s: s['name'])}
