"""Fail-closed, selective lesion diagnosis. Detector scores are not probabilities."""
from dataclasses import dataclass
from pathlib import Path
import io
import math
import json
import threading

from .common import FALLBACK, sha256


@dataclass(frozen=True)
class Policy:
    confidence: float = .80
    min_area_pixels: int = 64
    leaf_score: float = .95
    blur_threshold: float = 100.
    extreme_fraction: float = .65
    min_dimension: int = 224
    max_pixels: int = 20_000_000
    max_bytes: int = 10_000_000
    image_size: int = 1024

    def __post_init__(self):
        if not .8 <= self.confidence <= 1 or not 0 < self.leaf_score <= 1:
            raise ValueError('Invalid confidence thresholds')
        if any(not math.isfinite(v) or v < 1 for v in (self.min_area_pixels, self.max_pixels, self.min_dimension, self.max_bytes, self.image_size)):
            raise ValueError('Invalid size limits')
        if not 0 < self.extreme_fraction <= 1 or not math.isfinite(self.blur_threshold) or self.blur_threshold <= 0:
            raise ValueError('Invalid quality thresholds')


def quality_gate(image, policy):
    import cv2
    # Check blur at a canonical maximum side to reduce camera-resolution dependence.
    h, w = image.shape[:2]
    if min(h, w) < policy.min_dimension:
        return 'too_small'
    scale = min(1., policy.image_size/max(h, w))
    image = cv2.resize(image, (round(w*scale), round(h*scale)))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    if float((gray < 15).mean()) > policy.extreme_fraction:
        return 'underexposed'
    if float((gray > 245).mean()) > policy.extreme_fraction:
        return 'overexposed'
    if cv2.Laplacian(gray, cv2.CV_64F).var() < policy.blur_threshold:
        return 'blurred'
    return None


def uncertain(reason):
    return {'status': 'uncertain', 'reason': reason, 'message': FALLBACK, 'lesions': []}


class Engine:
    def __init__(self, weights, gate_directory, policy=Policy(), device='cpu'):
        import numpy as np
        import torch
        from ultralytics import YOLO
        from .gate import LeafGate, transform
        self.policy, self.device, self.lock = policy, device, threading.Lock()
        for path in (Path(weights), Path(gate_directory)/'leaf_gate.pt', Path(gate_directory)/'ood.npz'):
            if not path.is_file():
                raise ValueError(f'Missing trained artifact: {path}')
        self.detector = YOLO(str(weights))
        if self.detector.task not in ('detect', 'segment'):
            raise ValueError('Only lesion detection / segmentation models are supported')
        self.gate = LeafGate().to(device).eval()
        self.gate.load_state_dict(torch.load(Path(gate_directory)/'leaf_gate.pt', map_location=device, weights_only=True))
        with np.load(Path(gate_directory)/'ood.npz', allow_pickle=False) as bank:
            self.mean, self.variance, self.ood_limit = bank['mean'], bank['variance'], float(bank['threshold'])
        if self.mean.shape != (512,) or self.variance.shape != (512,) or not np.all(self.variance > 0):
            raise ValueError('Invalid OOD bank')
        if not np.isfinite(self.mean).all() or not np.isfinite(self.variance).all() or not np.isfinite(self.ood_limit):
            raise ValueError('Nonfinite OOD statistics')
        self.transform = transform()
        self.model_id = sha256(weights)

    def predict(self, raw):
        import cv2
        import numpy as np
        import torch
        from PIL import Image, ImageOps, UnidentifiedImageError
        from .gate import embedding_distance
        if not raw or len(raw) > self.policy.max_bytes:
            return uncertain('invalid_file_size')
        try:
            with Image.open(io.BytesIO(raw)) as uploaded:
                if uploaded.format not in ('JPEG', 'PNG', 'WEBP') or uploaded.width*uploaded.height > self.policy.max_pixels:
                    return uncertain('unsupported_image')
                image = ImageOps.exif_transpose(uploaded).convert('RGB')
                pixels = np.asarray(image)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            return uncertain('invalid_image')
        reason = quality_gate(pixels, self.policy)
        if reason:
            return uncertain(reason)
        with self.lock, torch.inference_mode():
            logits, features = self.gate(self.transform(image).unsqueeze(0).to(self.device))
            leaf_score = float(logits.softmax(-1)[0, 1])
            distance = float(embedding_distance(features.cpu().numpy(), self.mean, self.variance)[0])
            if not np.isfinite(leaf_score) or leaf_score < self.policy.leaf_score:
                return uncertain('not_a_supported_leaf')
            if not np.isfinite(distance) or distance > self.ood_limit:
                return uncertain('out_of_distribution')
            result = self.detector.predict(image, imgsz=self.policy.image_size,
                                           conf=self.policy.confidence, device=self.device, verbose=False)[0]
        lesions = []
        for index, box in enumerate(result.boxes):
            score = float(box.conf[0]); xyxy = box.xyxy[0].cpu().numpy()
            if not np.isfinite(score) or not np.isfinite(xyxy).all() or score < self.policy.confidence:
                continue
            area = float(max(0, xyxy[2]-xyxy[0])*max(0, xyxy[3]-xyxy[1]))
            if self.detector.task == 'segment':
                if result.masks is None:
                    continue
                # Rasterize in original image coordinates for an honest pixel-area threshold.
                polygon = result.masks.xy[index].astype(np.int32)
                mask = np.zeros(pixels.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [polygon], 1)
                area = int(mask.sum())
            if area < self.policy.min_area_pixels:
                continue
            cls = int(box.cls[0])
            lesions.append({'class_id': cls, 'label': result.names[cls], 'score': score,
                            'area_pixels': area, 'box': xyxy.tolist()})
        if not lesions:
            # No lesion is NOT a healthy diagnosis.
            return uncertain('no_reliable_lesion')
        return {'status': 'accepted', 'model_sha256': self.model_id, 'lesions': lesions,
                'message': 'Model finding; confirm locally before treatment.'}
