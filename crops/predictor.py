from functools import lru_cache

import joblib
import pandas as pd
from django.conf import settings

FIELD_RANGES = {
    'N': (0, 200), 'P': (0, 200), 'K': (0, 250),
    'temperature': (-5, 55), 'humidity': (0, 100), 'ph': (0, 14), 'rainfall': (0, 3500),
}


class ModelNotTrained(Exception):
    pass


@lru_cache(maxsize=1)
def _load():
    path = settings.ML_MODELS_DIR / 'crop_rf.joblib'
    if not path.exists():
        raise ModelNotTrained('Crop model not found. Run: python -m ml.train_crop')
    return joblib.load(path)


def recommend(values, top_n=3):
    """Return the top-N crops with probabilities for a dict of soil/climate values."""
    bundle = _load()
    model, features = bundle['model'], bundle['features']
    row = pd.DataFrame([[float(values[f]) for f in features]], columns=features)
    probs = model.predict_proba(row)[0]
    ranked = sorted(zip(model.classes_, probs), key=lambda p: p[1], reverse=True)[:top_n]
    return [{'crop': crop, 'probability': round(float(p), 3)} for crop, p in ranked]
