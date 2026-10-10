"""Crop yield inference (spec §3.4) using the model from ml/train_yield.py."""
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
from django.conf import settings

from .predictor import ModelNotTrained

DEFAULT_UNIT = 'tonnes/ha'


@lru_cache(maxsize=1)
def load_bundle():
    path = settings.ML_MODELS_DIR / 'yield_rf.joblib'
    if not path.exists():
        raise ModelNotTrained('Yield model not found. Run: python -m ml.train_yield')
    return joblib.load(path)


def predict_yield(crop, season, state, rainfall, area_ha=None):
    bundle = load_bundle()
    model = bundle['model']
    row = pd.DataFrame([{'Crop': crop, 'Season': season, 'State': state,
                         'Annual_Rainfall': float(rainfall), 'Crop_Year': bundle['latest_year']}])
    estimate = float(model.predict(row)[0])

    # Spread of individual trees (log scale) gives a likely range around the estimate.
    pipeline = model.regressor_
    features = pipeline[:-1].transform(row)
    tree_preds = np.expm1([tree.predict(features)[0] for tree in pipeline[-1].estimators_])
    low, high = np.percentile(tree_preds, [10, 90])

    unit = bundle['units'].get(crop, DEFAULT_UNIT)
    result = {
        'crop': crop, 'season': season, 'state': state, 'rainfall': float(rainfall),
        'yield_per_ha': round(estimate, 2), 'range_low': round(float(low), 2), 'range_high': round(float(high), 2),
        'unit': unit, 'historical_median': bundle['history'].get(f'{crop}|{state}'),
        'season_typical': season in bundle['crop_seasons'].get(crop, []),
    }
    if area_ha:
        result['area_ha'] = float(area_ha)
        result['total'] = round(estimate * float(area_ha), 2)
        result['total_unit'] = unit.removesuffix('/ha')
    return result
