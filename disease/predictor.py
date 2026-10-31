"""Trained ML Deep Learning inference engine for leaf disease diagnosis.

Loads and executes ml/models/disease_cnn.keras against leaf photographs
without any external API calls.
"""
import io
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from django.conf import settings
from PIL import Image

from .gemini import DiagnosisError
from .treatments import (
    advice_for,
    get_diagnosis_details,
    parse_class,
)

IMG_SIZE = (64, 64)

ModelNotTrained = DiagnosisError


@lru_cache(maxsize=1)
def _load_model():
    """Load the trained Keras CNN model and class label mapping."""
    models_dir = getattr(settings, 'ML_MODELS_DIR', None)
    if not models_dir:
        models_dir = settings.BASE_DIR / 'ml' / 'models'

    model_path = Path(models_dir) / 'disease_cnn.keras'
    classes_path = Path(models_dir) / 'disease_classes.json'

    if not model_path.exists() or not classes_path.exists():
        raise DiagnosisError(
            'Disease ML model not found. Trained model file ml/models/disease_cnn.keras is required.',
            code='model_not_found',
            status=500
        )

    try:
        from tensorflow import keras
        model = keras.models.load_model(model_path)
        classes = json.loads(classes_path.read_text(encoding='utf-8'))
        return model, classes
    except Exception as exc:
        raise DiagnosisError(
            f'Failed to initialize ML disease model: {exc}',
            code='model_init_error',
            status=500
        ) from exc


def predict(image_file, crop='', location='', notes='', language='en'):
    """Analyze leaf photograph using trained CNN deep learning model.

    Args:
        image_file: File-like object, PIL Image, or UploadedFile containing the leaf photo.
        crop: Optional crop or plant name provided by user or context.
        location: Optional user field location.
        notes: Optional field observations.
        language: Language code for localization.

    Returns:
        dict: Full diagnosis report matching UI requirements.
    """
    model, classes = _load_model()

    try:
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        if isinstance(image_file, Image.Image):
            img = image_file.convert('RGB')
        else:
            img = Image.open(image_file).convert('RGB')
    except Exception as exc:
        raise DiagnosisError(
            'The uploaded file is not a valid or readable image. Please provide a clear JPG or PNG photo.',
            code='invalid_image',
            status=400
        ) from exc

    # Resize to model input shape (64, 64)
    img_resized = img.resize(IMG_SIZE)
    arr = np.asarray(img_resized, dtype='float32')
    batch = np.expand_dims(arr, 0)

    # Run neural network inference
    probs = model.predict(batch, verbose=0)[0]

    # Sort prediction indices descending by confidence
    top_indices = np.argsort(probs)[::-1]
    top_idx = int(top_indices[0])
    top_class = classes[top_idx]
    top_confidence = float(probs[top_idx])

    # Extract secondary predictions as alternatives
    alternatives = []
    for idx in top_indices[1:5]:
        p = float(probs[idx])
        if p >= 0.04:  # At least 4% probability
            c = classes[int(idx)]
            plant, disease = parse_class(c)
            disease_name = disease.title() if disease != 'healthy' else 'Healthy Leaf'
            alternatives.append({
                'class': c,
                'plant': plant,
                'disease': disease_name,
                'confidence': round(p, 4)
            })

    # Build rich diagnosis result dictionary
    result = get_diagnosis_details(
        class_name=top_class,
        confidence=top_confidence,
        crop_context=crop,
        location=location,
        notes=notes,
        alternatives=alternatives
    )

    return result


# Direct compatibility alias
analyze_leaf = predict

__all__ = ['predict', 'analyze_leaf', 'DiagnosisError', 'ModelNotTrained', '_load_model']
