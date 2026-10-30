# Field-domain leaf disease pipeline

Standalone implementation of `codex.md`. No existing web application files are modified. This is an engineering pipeline, **not a trained, validated diagnostic product**. Neither >95% precision nor zero false confidence is guaranteed. Production deployment is blocked until an independently measured release report passes its criteria.

## Layout

| Module | Files |
|---|---|
| Dataset integration and background decoupling | `import_sources.py`, `data.py`, `synthesize.py` |
| Outdoor augmentation and aspect-ratio preservation | `augment.py` |
| YOLO11 lesion detector / segmenter and negative classifier | `train.py`, `gate.py` |
| Input quality, OOD, selective prediction, authenticated API | `inference.py`, `serve.py` |
| mAP, PR plots, background FPR, uncertainty intervals, EigenCAM | `evaluate.py`, `audit_cam.py` |

Run commands below **from the repository root**. All datasets, environments and artifacts stay under `field_vision/`.

## 1. Environment and data

Use Python 3.11 or 3.12. GPU training is recommended; start with `yolo11m.pt` for lower memory use. Install the appropriate PyTorch CUDA build for your machine if necessary. The versions in `requirements.txt` are a compatibility baseline, not a claim that these are the latest packages or a security-audited lockfile.

```sh
python3.12 -m venv field_vision/.venv
field_vision/.venv/bin/pip install -r field_vision/requirements.txt
field_vision/.venv/bin/python -m unittest discover -s field_vision/tests -v
```

Download data through the dataset owner's distribution, accepting its terms. No credentials, third-party data, or trained weights are included.

- [PlantDoc original detection release](https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset): stage TRAIN/TEST images, retain source class metadata and original split provenance. Inspect annotations: **a diseased-leaf box is not a lesion box**. Add expert-reviewed lesion annotations rather than relabeling an entire leaf as a lesion.
- FieldPlant: obtain the authors' original release, preserve capture/plant identifiers and original annotation files, and stage the extracted image directory. Confirm annotation granularity and permitted use with the release documentation; no guessed mirror or automated download is embedded.
- [Kaggle Cassava](https://www.kaggle.com/competitions/cassava-leaf-disease-classification/data) and [FGVC iCassava](https://arxiv.org/abs/1908.02900): download using your own account/approved access. Image-level classes support sampling and annotation review, **not automatic lesion ground truth**. For CSVs with different column names, normalize to `image_id,label` first.

```sh
field_vision/.venv/bin/python -m field_vision.import_sources plantdoc field_vision/data/raw/PlantDoc field_vision/data/plantdoc-review.jsonl
field_vision/.venv/bin/python -m field_vision.import_sources fieldplant field_vision/data/raw/FieldPlant field_vision/data/fieldplant-review.jsonl
field_vision/.venv/bin/python -m field_vision.import_sources cassava field_vision/data/raw/cassava field_vision/data/cassava-review.jsonl --metadata field_vision/data/raw/cassava/train.csv
```

The staging script intentionally writes unusable split/group placeholders. Assign groups by farm, plant and capture session, then partition them into train/validation/test **before augmentation**. Use a global group namespace across datasets. Resolve duplicates and near-duplicates across sources manually; the importer additionally checks exact hashes and group leakage. Retain one independent image per group for release evaluation so repeated frames do not inflate confidence intervals.

Annotation schema, one object per JSONL line (paths relative to the JSONL):

```json
{"image":"raw/leaf001.jpg","label":"labels/leaf001.txt","kind":"leaf","group":"farmA-plant7-capture1","split":"train","source":"fieldplant","domain":"field","annotation_scope":"lesion_reviewed"}
```

Use a consistent **crop + disease** class taxonomy. YOLO detection rows: `class xc yc width height`; segmentation rows: `class x1 y1 x2 y2 x3 y3 ...`. All coordinates are normalized. Annotate lesion regions, not uniform-background outlines. Dense / diffuse symptoms may not form distinct lesions: validate whether this approach is suitable for each disease rather than forcing misleading boxes. Polygon holes are not represented by this format.

For healthy leaves, experts must provide an explicit empty label file. For negative objects (hands, shoes, soil, equipment, supported-scope-negative grass), use `kind: background`, an absent or empty label, a real capture group and a held-out split. The detector learns negatives from **empty labels**, not a giant background bounding box; a separate classifier explicitly learns `background` versus `leaf`.

```sh
field_vision/.venv/bin/python -m field_vision.data field_vision/data/reviewed.jsonl field_vision/data/prepared --task segment --names tomato_early_blight tomato_late_blight
```

This creates `images/{train,val,test}`, `labels/{train,val,test}`, `gate/{train,val,test}/{background,leaf}`, `dataset.yaml`, and provenance. Negative/healthy examples must occur in every split. Normalize EXIF orientation before annotation; the importer refuses rotated EXIF metadata to avoid misaligned labels.

## 2. Synthetic backgrounds and outdoor augmentation

Supply at least **2,000 distinct licensed training-only** background photos: soil, hands, sky, sunlight, weeds and stems. Never reuse validation/test backgrounds. The rembg foreground mask is not a lesion mask. Lesion annotation coordinates remain unchanged during compositing.

```sh
field_vision/.venv/bin/python -m field_vision.synthesize field_vision/data/reviewed.jsonl field_vision/data/background-bank field_vision/data/synthetic --copies 3
```

`rembg` may download its U2Net weights on first execution. Provision/cache them before offline use. Review every generated composite and `.mask.png`, especially chlorotic margins and lesions accidentally erased by segmentation. Generated records are marked `needs_mask_review` and are rejected by training import until reviewed. Merge approved train-only records into the manifest, retain their original group, and reimport to a **new** prepared directory.

```sh
field_vision/.venv/bin/python -m field_vision.augment field_vision/data/prepared field_vision/data/augmented --task segment --size 1024 --copies 2
```

Lighting, shadows, blur, ISO/Gaussian noise, cutout and geometry affect image/masks together. Letterboxing avoids aspect-ratio distortion. Fully occluded lesions are removed; segmentation fragments are relabeled as visible components. Validation/test sets are copied unchanged. Inspect augmentation grids before training: very aggressive augmentations can erase diagnostic morphology. Keep original field samples and tune synthetic/field balance per disease. The gate dataset intentionally uses original inputs, not artificial lesion fragments.

## 3. Train

```sh
field_vision/.venv/bin/python -m field_vision.train field_vision/data/augmented/dataset.yaml --task segment --weights yolo11x-seg.pt --device 0 --batch 2
# Alternative detection-only run (requires a detection-format dataset):
# ... --task detect --weights yolo11m.pt
field_vision/.venv/bin/python -m field_vision.gate field_vision/data/prepared/gate field_vision/artifacts/gate --device cuda --pretrained
```

Ultralytics may download requested pretrained weights. Preserve run configuration, data provenance and artifact hashes. Small-lesion settings use 1024 input, mask ratio 1, no overlapping mask downsampling, and configurable built-in box/DFL weights. YOLO11's decoupled heads and native losses are used; this does **not** pretend a novel loss removes background interference. Check small-lesion recall at native camera scales and stratify by crop, disease, site and device.

The explicit background classifier uses weighted cross entropy. The OOD bank fits diagonal feature distances on training leaves and a 99th-percentile cutoff on validation leaves. This is an empirical rejection heuristic, not a universal OOD detector. Include unsupported crops, non-leaf objects and unseen disease appearances in adversarial testing. Use field validation to tune thresholds and freeze them before test evaluation. ResNet is used **only as the input/background gate**, not the disease classifier.

## 4. Audit and release

```sh
field_vision/.venv/bin/python -m field_vision.evaluate field_vision/data/reviewed.jsonl field_vision/data/prepared/dataset.yaml field_vision/runs/lesions/weights/best.pt field_vision/artifacts/gate field_vision/artifacts/test-audit --task segment --device 0
field_vision/.venv/bin/python -m field_vision.audit_cam field_vision/runs/lesions/weights/best.pt field_vision/data/test-leaf.jpg field_vision/data/test-lesion-mask.png field_vision/artifacts/cam
```

Evaluation produces raw-model box/mask mAP@0.5 and mAP@0.5:0.95, precision/recall metrics and PR plots, plus deployed-policy coverage, conservative accepted-image precision, false-positive rate on pure backgrounds, Wilson intervals and source breakdowns. An accepted image counts as correct only when every reported lesion has a class-correct unique ground-truth box match at IoU >= .5; missed lesions are measured separately by raw-model recall. No acceptance means uncertainty, **not healthy**. Raw detector metrics and the selective pipeline metrics measure different things.

The default release policy requires at least 100 accepted independent images, at least 300 independent negatives, a 95% Wilson lower bound on selective precision above .95, and a background FPR upper bound below .02. These are explicit baseline criteria; agree on application-specific coverage, subgroup recall and false-positive tolerances before release. A tiny accepted subset can have high precision and poor utility. Never tune on the final test set. `--split val --policy path.json` supports validation experiments; validation reports cannot unlock deployment.

EigenCAM saves both PCA signs and reports attribution mass inside a supplied expert lesion mask. It is class-agnostic and cannot prove the model ignores backgrounds. Audit lesion versus soil/finger masks, compare background-swapped pairs and run lesion-occlusion controls. A convincing heatmap alone is insufficient evidence.

## 5. Serve

```sh
export VISION_WEIGHTS="$PWD/field_vision/runs/lesions/weights/best.pt"
export VISION_GATE="$PWD/field_vision/artifacts/gate"
export VISION_REPORT="$PWD/field_vision/artifacts/test-audit/report.json"
export VISION_API_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
field_vision/.venv/bin/uvicorn field_vision.serve:app --host 127.0.0.1 --port 8080 --workers 1 --limit-concurrency 8
```

`POST /predict`: multipart `file`, header `Authorization: Bearer <key>`. Startup fails without a passing **test** report or when any model/gate/OOD artifact hash differs from the evaluated artifacts. Keep reports and weights read-only and administrator-controlled; a JSON report is not a cryptographic attestation. Do not load untrusted `.pt` files.

Before inference: byte/pixel/dimension limits, format validation, EXIF normalization, luminance histogram checks and Laplacian variance (<100 default) rejection. Thresholds depend on camera resolution and field data. After gating: empirical OOD rejection, detector score >= .80 and lesion pixel-area cutoff. A detection score is not a calibrated disease probability. Rejections return exactly:

> Uncertain diagnosis. Please capture the leaf closer, in indirect daylight, and steady the camera.

Use TLS and an authenticated, rate-limiting reverse proxy; cap request bodies at 10 MB before multipart parsing, set timeouts, and bind direct service access to a private network. One inference worker serializes GPU/model access. Add resource-based autoscaling only after load testing. Logs contain request IDs/status, not uploaded images. Training/inference failures do not manufacture diagnoses.

Container build: `docker build -f field_vision/Dockerfile -t field-vision .`. Mount trained artifacts read-only and pass the environment variables above. The Dockerfile copies only module source files, not local environments or datasets. GPU containers require an appropriate CUDA/PyTorch base instead of the example CPU-oriented image.

## Verification scope

Dependency-free contract tests and compilation are provided. No field data or annotated lesion weights were supplied; no training, disease-accuracy claim, deployment benchmark, or enterprise certification has been performed. The service is deliberately separate from the existing Django website.

References: [YOLO11](https://docs.ultralytics.com/models/yolo11/), [training arguments](https://docs.ultralytics.com/modes/train/), [Albumentations](https://albumentations.ai/docs/api-reference/), [rembg](https://github.com/danielgatis/rembg), [EigenCAM reference](https://github.com/jacobgil/pytorch-grad-cam). Review library/model/data licenses before distributing a commercial deployment.
