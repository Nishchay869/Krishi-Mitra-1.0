"""Generate bundled translations using a local MLX model, with network access disabled."""
import argparse
import json
import os
from pathlib import Path
import re
import time
import unicodedata
import runpy

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = {
    'as': 'Assamese', 'bn': 'Bengali', 'brx': 'Bodo', 'doi': 'Dogri',
    'gu': 'Gujarati', 'hi': 'Hindi', 'kn': 'Kannada', 'ks': 'Kashmiri',
    'kok': 'Konkani', 'mai': 'Maithili', 'ml': 'Malayalam', 'mni': 'Manipuri',
    'mr': 'Marathi', 'ne': 'Nepali', 'or': 'Odia', 'pa': 'Punjabi',
    'sa': 'Sanskrit', 'sat': 'Santali', 'sd': 'Sindhi', 'ta': 'Tamil',
    'te': 'Telugu', 'ur': 'Urdu',
}
TOKENS = re.compile(r'%\([^)]+\)[a-z]|R²')
NUMBERS = re.compile(r'\d+(?:\.\d+)?')


MEDICAL_MESSAGES = set(runpy.run_path(str(ROOT / 'disease/treatments.py'))['TREATMENTS'].values())

CRITICAL = re.compile(
    r'grams per litre of water|ml per litre of water|\b(?:WP|EC|SC)\b|%\([^)]+\)[a-z]|R²|copper oxychloride|captan|mancozeb|hexaconazole|'
    r'propiconazole|cymoxanil|metalaxyl|streptocycline|spiromesifen|imidacloprid|'
    r'chlorothalonil|sulphur|\d+(?:\.\d+)?', re.IGNORECASE)


# Keep a complete product/formulation/dose together. Translation must not detach
# a number or a litre denominator from the product it belongs to.
PROTOCOL = re.compile(
    r'(?P<drug>captan or mancozeb|cymoxanil \+ mancozeb|metalaxyl \+ mancozeb|'
    r'wettable sulphur|copper oxychloride|captan|mancozeb|propiconazole|hexaconazole|'
    r'chlorothalonil|streptocycline|spiromesifen|neem oil)'
    r'(?:\s+\d+(?:\.\d+)?%\s*(?:wettable powder|emulsifiable concentrate|suspension concentrate)?\s*\((?P<formulation>[^)]+)\))?'
    r'\s+at\s+(?P<dose>\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s+(?P<unit>grams|ml) per litre of water',
    re.IGNORECASE)
STRICT_TOKENS = re.compile(PROTOCOL.pattern + '|' + CRITICAL.pattern, re.IGNORECASE)


def protocol_label(text):
    match = PROTOCOL.fullmatch(text)
    if not match:
        return text
    drug = match['drug'].removeprefix('wettable ')
    formulation = ' ' + match['formulation'] if match['formulation'] else ''
    unit = 'g/L' if match['unit'] == 'grams' else 'mL/L'
    return f"{drug}{formulation}: {match['dose']} {unit}"


def protect(source, strict=False, style='digits'):
    tokens = {}
    def replace(match):
        marker = f'<ph{len(tokens)}/>' if style == 'xml' else str(8675309001 + len(tokens))
        tokens[marker] = protocol_label(match.group())
        return marker
    return (STRICT_TOKENS if strict else TOKENS).sub(replace, source).replace('%%', '%'), tokens


def validate(source, translated, tokens):
    translated = ''.join(str(unicodedata.decimal(ch)) if ch.isdecimal() else ch for ch in translated).strip()
    translated = re.sub(r'(?<=\d)\s*\.\s*(?=\d)', '.', translated)
    if not translated:
        raise ValueError('Empty translation')
    if '\ufffd' in translated:
        raise ValueError('Invalid Unicode output')
    for marker, token in tokens.items():
        pattern = r'\s*'.join(re.escape(ch) for ch in marker)
        if len(re.findall(pattern, translated, flags=re.IGNORECASE)) != 1:
            raise ValueError('Changed formatting token')
        translated = re.sub(pattern, lambda _: token, translated, count=1, flags=re.IGNORECASE)
    if re.search(r'<\s*ph\d', translated, flags=re.IGNORECASE):
        raise ValueError('Unexpected placeholder in output')
    words = translated.split()
    if any(words.count(word) > max(5, len(words) // 3) for word in set(words)):
        raise ValueError('Excessive repetition')
    if len(translated) > max(100, len(source) * 8):
        raise ValueError('Unexpected translation length')
    if '%(' in source:
        translated = re.sub(r'(?<!%)%(?!\([^)]+\)[a-z]|%)', '%%', translated)
    from collections import Counter
    expected, actual = Counter(NUMBERS.findall(source)), Counter(NUMBERS.findall(translated))
    # A formulation's concentration may be written once instead of twice, e.g.
    # '80% wettable powder (80 WP)' -> '80% wettable powder'. Doses remain strict.
    for number in re.findall(r'(\d+(?:\.\d+)?)%[^.]*?\(\1 (?:WP|EC|SC)\)', source):
        if expected[number] - actual[number] == 1:
            expected[number] -= 1
    if expected != actual:
        raise ValueError('Changed numeric value')
    return translated


def write_json(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=ROOT / '.offline-models/sarvam-translate-4bit')
    parser.add_argument('--languages', nargs='+', choices=LANGUAGES, default=list(LANGUAGES))
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--strict-protection', action='store_true', help='Also preserve every numeric value and chemical name while retrying rejected messages.')
    parser.add_argument('--limit', type=int, help='Limit messages for a local smoke test.')
    args = parser.parse_args()
    model_path = args.model.resolve()
    if not model_path.is_dir() or not (model_path / 'config.json').exists():
        parser.error('Download the model once first; --model must point to an existing local model directory.')
    import mlx.core as mx
    mx.set_cache_limit(128 * 1024 * 1024)
    from mlx_lm import load
    from mlx_lm.generate import batch_generate
    from mlx_lm.sample_utils import make_sampler, make_logits_processors
    print('Loading local model (internet disabled)...', flush=True)
    model, tokenizer = load(str(model_path), trust_remote_code=False)
    source = json.loads((ROOT / 'locale/ui/en.json').read_text())
    started = time.monotonic()
    for code in args.languages:
        path = ROOT / f'locale/ui/{code}.json'
        if path.exists() and source.keys() <= json.loads(path.read_text()).keys():
            print(f'{code}: bundled catalog already complete', flush=True)
            continue
        draft = ROOT / f'locale/drafts/{code}.json'
        draft.parent.mkdir(exist_ok=True)
        catalog = json.loads(draft.read_text()) if draft.exists() else {}
        overrides_path = ROOT / f'locale/overrides/{code}.json'
        if overrides_path.exists():
            for key, value in json.loads(overrides_path.read_text()).items():
                if key in source:
                    catalog[key] = validate(key, value, {})
        review_path = draft.parent / f'{code}.review.json'
        previous_review = json.loads(review_path.read_text()) if review_path.exists() else {}
        if 'Yield Estimate' in previous_review and catalog.get('Yield prediction'):
            catalog['Yield Estimate'] = catalog['Yield prediction']
        failed = {}
        pending = sorted((key for key in source if not catalog.get(key)), key=len)
        if args.limit:
            pending = pending[:args.limit]
        batches = []
        offset = 0
        while offset < len(pending):
            length = len(pending[offset])
            capacity = min(args.batch_size, 32 if length < 80 else 8 if length < 180 else 4)
            keys = pending[offset:offset + capacity]
            batches.append(keys)
            offset += len(keys)
        for keys in batches:
            protected = [protect(key, strict=args.strict_protection or key in MEDICAL_MESSAGES or key in previous_review, style='xml' if code in {'mni', 'sat'} else 'digits') for key in keys]
            prompts = []
            limits = []
            for key, (text, _) in zip(keys, protected):
                if key == 'Rabi' and key in previous_review:
                    text = '"Rabi" (crop season)'
                prompt = tokenizer.apply_chat_template([
                    {'role': 'system', 'content': f'Target language: {LANGUAGES[code]}'},
                    {'role': 'user', 'content': text},
                ], tokenize=False, add_generation_prompt=True)
                # This pinned conversion's template omits the assistant-turn marker.
                # Without it Gemma may end the user turn or repeat short labels.
                if not prompt.endswith('<start_of_turn>model\n'):
                    prompt += '<start_of_turn>model\n'
                prompts.append(tokenizer.encode(prompt, add_special_tokens=False))
                limits.append(min(1800, max(256, len(tokenizer.encode(text)) * 16 + 64)) if code in {'mni', 'sat'} else min(640, max(32, len(tokenizer.encode(text)) * 4 + 16)))
            result = batch_generate(model, tokenizer, prompts, max_tokens=limits,
                                    return_token_ids=True,
                                    sampler=make_sampler(temp=0.01),
                                    logits_processors=make_logits_processors(repetition_penalty=1.1, repetition_context_size=32),
                                    prefill_batch_size=len(keys), completion_batch_size=args.batch_size)
            for key, output, (_, tokens), ids, limit in zip(keys, result.texts, protected, result.token_ids, limits):
                try:
                    if len(ids) >= limit:
                        raise ValueError('Output truncated')
                    catalog[key] = validate(key, output, tokens)
                except ValueError as exc:
                    failed[key] = {'reason': str(exc), 'output': output}
            mx.clear_cache()
            write_json(draft, catalog)
            (draft.parent / f'{code}.review.json').write_text(json.dumps(failed, ensure_ascii=False, indent=2) + '\n')
            print(f'{code}: {len(catalog)}/{len(source)} saved; {len(failed)} need review; '
                  f'{time.monotonic()-started:.0f}s elapsed', flush=True)
        if failed:
            (draft.parent / f'{code}.review.json').write_text(json.dumps(failed, ensure_ascii=False, indent=2) + '\n')
        if source.keys() <= catalog.keys():
            write_json(path, catalog)
            provenance_path = ROOT / 'locale/translation-provenance.json'
            provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
            provenance[code] = {'method': 'local-model',
                                'model': 'mlx-community/sarvam-translate-mlx-4bit',
                                'revision': '7c664b5203a0db7f6d1e8a0c0a2a0d76c8f41e64',
                                'source_messages': len(source), 'api_calls': 0}
            provenance_path.write_text(json.dumps(provenance, indent=2) + '\n')
            print(f'{code}: complete local catalog saved', flush=True)
    print('Generation finished. Run python scripts/build_translations.py to compile complete catalogs.', flush=True)


if __name__ == '__main__':
    main()
