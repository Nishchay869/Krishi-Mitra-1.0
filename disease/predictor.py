import json
from functools import lru_cache

import numpy as np
from django.conf import settings
from PIL import Image

from .treatments import advice_for

IMG_SIZE = (64, 64)


class ModelNotTrained(Exception):
    pass


@lru_cache(maxsize=1)
def _load():
    model_path = settings.ML_MODELS_DIR / 'disease_cnn.keras'
    classes_path = settings.ML_MODELS_DIR / 'disease_classes.json'
    if not model_path.exists() or not classes_path.exists():
        raise ModelNotTrained(
            'Disease model not trained yet. Install requirements-ml.txt, download PlantVillage '
            'into data/plantvillage and run: python -m ml.train_disease'
        )
    try:
        from tensorflow import keras
    except ImportError as exc:
        raise ModelNotTrained('TensorFlow is not installed. Run: pip install -r requirements-ml.txt') from exc
    return keras.models.load_model(model_path), json.loads(classes_path.read_text())


def predict(image_file):
    model, classes = _load()
    img = Image.open(image_file).convert('RGB').resize(IMG_SIZE)
    batch = np.expand_dims(np.asarray(img, dtype='float32'), 0)  # model rescales internally
    probs = model.predict(batch, verbose=0)[0]
    idx = int(probs.argmax())
    result = advice_for(classes[idx])
    result.update(label=classes[idx], confidence=round(float(probs[idx]), 3))
    return result
