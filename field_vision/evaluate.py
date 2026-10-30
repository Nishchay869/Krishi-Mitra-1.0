"""Independent field-test audit: raw model mAP + deployed-policy risk/coverage."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

from .common import read_manifest, sha256, wilson
from .inference import Engine, Policy


def iou(a, b):
    x = max(0, min(a[2], b[2])-max(a[0], b[0]))
    y = max(0, min(a[3], b[3])-max(a[1], b[1]))
    intersection = x*y
    union = max(0,a[2]-a[0])*max(0,a[3]-a[1])+max(0,b[2]-b[0])*max(0,b[3]-b[1])-intersection
    return intersection/union if union else 0.


def correctly_localized(predictions, truth):
    # One-to-one matching prevents duplicate detections earning extra credit.
    unmatched = list(truth)
    for prediction in sorted(predictions, key=lambda p: p['score'], reverse=True):
        options = [(iou(prediction['box'], box), index) for index, (cls, box) in enumerate(unmatched)
                   if cls == prediction['class_id']]
        if not options or max(options)[0] < .5:
            return False
        unmatched.pop(max(options)[1])
    return bool(predictions)


def summarize(records):
    accepted = [r for r in records if r['accepted']]
    correct = sum(r['correct'] for r in accepted)
    negatives = [r for r in records if r['negative']]
    false_alarms = sum(r['accepted'] for r in negatives)
    precision_ci = wilson(correct, len(accepted))
    fpr_ci = wilson(false_alarms, len(negatives))
    return {'images': len(records), 'accepted': len(accepted), 'negative_images': len(negatives),
            'coverage': len(accepted)/len(records) if records else 0.,
            'selective_precision': correct/len(accepted) if accepted else None,
            'precision_wilson_95': precision_ci,
            'background_fpr': false_alarms/len(negatives) if negatives else None,
            'background_fpr_wilson_95': fpr_ci,
            # These are explicit example release criteria, not universal safety guarantees.
            'release_passed': len(accepted) >= 100 and len(negatives) >= 300
                              and precision_ci[0] > .95 and fpr_ci[1] < .02}


def main():
    from PIL import Image
    import numpy as np
    p = argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('dataset_yaml')
    p.add_argument('weights'); p.add_argument('gate_directory'); p.add_argument('output')
    p.add_argument('--task', choices=['detect', 'segment'], default='segment')
    p.add_argument('--split', choices=['val', 'test'], default='test')
    p.add_argument('--policy'); p.add_argument('--device', default='cpu')
    a = p.parse_args(); out = Path(a.output); out.mkdir(parents=True, exist_ok=False)
    policy = Policy(**json.loads(Path(a.policy).read_text())) if a.policy else Policy()
    engine = Engine(a.weights, a.gate_directory, policy, a.device)
    if engine.detector.task != a.task:
        raise ValueError('Task must match the trained model')
    rows = [r for r in read_manifest(a.manifest) if r['split'] == a.split]
    if not rows or any(r.get('domain') != 'field' or r['source'] == 'synthetic' for r in rows):
        raise ValueError('Evaluation requires real field images; synthetic validation is not a release test')
    if len({r['group'] for r in rows}) != len(rows) or len({sha256(r['image']) for r in rows}) != len(rows):
        raise ValueError('Release audit requires one independent sample per group and no duplicate images')
    records = []
    for row in rows:
        if row['kind'] == 'leaf' and (row.get('annotation_scope') != 'lesion_reviewed' or not row.get('label')):
            raise ValueError('Evaluation requires reviewed annotations')
        with Image.open(row['image']) as image:
            w, h = image.size
        truth = []
        text = Path(row['label']).read_text() if row.get('label') else ''
        for line in text.splitlines():
            if not line.strip():
                continue
            fields = line.split(); cls, xy = int(fields[0]), np.array(fields[1:], dtype=float)
            if a.task == 'detect':
                x,y,bw,bh = xy; box = [(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h]
            else:
                points = xy.reshape(-1, 2)*[w,h]
                box = [*points.min(0), *points.max(0)]
            truth.append((cls, box))
        result = engine.predict(Path(row['image']).read_bytes())
        accepted = result['status'] == 'accepted'
        records.append({'image_sha256': sha256(row['image']), 'source': row['source'],
                        'group': row['group'], 'negative': row['kind'] == 'background',
                        'accepted': accepted, 'correct': correctly_localized(result['lesions'], truth),
                        'reason': result.get('reason'), 'lesions': result['lesions']})
    metrics = engine.detector.val(data=a.dataset_yaml, split=a.split, imgsz=policy.image_size,
                                  device=a.device, conf=.001, plots=True, project=str(out), name='yolo_metrics')
    report = {**summarize(records), 'split': a.split, 'policy': asdict(policy),
              'manifest_sha256': sha256(a.manifest),
              'artifacts': {'weights': sha256(a.weights),
                            'leaf_gate': sha256(Path(a.gate_directory)/'leaf_gate.pt'),
                            'ood': sha256(Path(a.gate_directory)/'ood.npz')},
              'raw_model_metrics': {k: float(v) for k,v in metrics.results_dict.items()},
              'by_source': {s: summarize([r for r in records if r['source']==s])
                            for s in sorted({r['source'] for r in records})}}
    if a.split != 'test':
        report['release_passed'] = False
    (out/'report.json').write_text(json.dumps(report, indent=2))
    (out/'predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    print(json.dumps({k:report[k] for k in ('coverage','selective_precision','background_fpr','release_passed')}, indent=2))


if __name__ == '__main__':
    main()
