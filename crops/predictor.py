from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from django.conf import settings

from .crop_metadata import INDIAN_CROPS_METADATA

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


@lru_cache(maxsize=1)
def _load_centroids():
    csv_path = settings.BASE_DIR / 'data' / 'crop_recommendation.csv'
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    if not csv_path.exists():
        return None, None
    df = pd.read_csv(csv_path)
    means = df.groupby('label')[features].mean()
    overall_std = df[features].std().replace(0, 1)
    return means, overall_std


def _compute_match_grade(prob: float) -> tuple[str, str]:
    """Return (grade_badge_text, badge_class)."""
    if prob >= 0.80:
        return 'Exceptional Match', 'crop-badge-grade-exceptional'
    if prob >= 0.60:
        return 'High Suitability', 'crop-badge-grade-high'
    if prob >= 0.40:
        return 'Good Alternative', 'crop-badge-grade-good'
    return 'Viable Option', 'crop-badge-grade-viable'


def recommend(values, top_n=3):
    """Return the top-N crops with probabilities and rich agronomic intelligence for a dict of soil/climate values."""
    bundle = _load()
    model, features = bundle['model'], bundle['features']

    # Vectorize input
    x_vec = np.array([float(values[f]) for f in features])
    row = pd.DataFrame([x_vec], columns=features)
    rf_probs = dict(zip(model.classes_, model.predict_proba(row)[0]))

    # Load pre-calculated agronomic centroids
    means, overall_std = _load_centroids()
    weights = np.array([0.7, 0.7, 0.7, 1.5, 1.0, 1.5, 1.2])

    scored = []
    classes = list(model.classes_) if means is None else list(means.index)

    for crop in classes:
        rf_p = float(rf_probs.get(crop, 0.0))

        if means is not None and crop in means.index:
            mu = means.loc[crop].values
            diff = (x_vec - mu) / overall_std.values
            dist = float(np.sqrt(np.sum(weights * (diff ** 2))))
            agro_affinity = float(np.exp(-dist / 3.2))
        else:
            agro_affinity = rf_p

        # Combine ML confidence with agronomic tolerance distance
        if rf_p >= 0.50:
            combined = 0.85 * rf_p + 0.15 * agro_affinity
            display_prob = round(rf_p, 3)
        elif rf_p > 0.05:
            combined = 0.60 * rf_p + 0.40 * agro_affinity
            display_prob = round(0.50 * rf_p + 0.50 * agro_affinity, 3)
        else:
            combined = 0.20 * rf_p + 0.80 * agro_affinity
            display_prob = round(agro_affinity * 0.80, 3)

        scored.append((crop, combined, display_prob))

    scored.sort(key=lambda item: item[1], reverse=True)
    top_candidates = scored[:top_n]

    results = []
    for rank_idx, (crop, _, display_prob) in enumerate(top_candidates, start=1):
        meta = INDIAN_CROPS_METADATA.get(crop, {})
        grade_text, grade_class = _compute_match_grade(display_prob)

        display_name = meta.get('name', crop.title())
        hindi_name = meta.get('hindi_name', '')
        emoji = meta.get('emoji', '🌱')
        category = meta.get('category', 'Crop')
        season = meta.get('season', 'Kharif / Rabi')
        soil_type = meta.get('soil_type', 'Well-drained agricultural soil')
        ideal_npk = meta.get('ideal_npk', 'Balanced NPK')
        ideal_ph = meta.get('ideal_ph', '6.0 – 7.5')
        ideal_temp = meta.get('ideal_temp', '20 – 30°C')
        ideal_rainfall = meta.get('ideal_rainfall', '50 – 150 mm')
        duration_days = meta.get('duration_days', '90 – 120 days')
        key_states = meta.get('key_states', 'Major agricultural states in India')
        why_message = meta.get('why_message', 'Well-aligned with your soil nutrient profile and climate conditions.')
        agronomic_tip = meta.get('agronomic_tip', 'Follow ICAR recommended nutrient and weed management schedules.')

        results.append({
            'crop': crop,
            'probability': display_prob,
            'percentage': int(round(display_prob * 100)),
            'rank': rank_idx,
            'name': display_name,
            'hindi_name': hindi_name,
            'emoji': emoji,
            'category': category,
            'season': season,
            'soil_type': soil_type,
            'ideal_npk': ideal_npk,
            'ideal_ph': ideal_ph,
            'ideal_temp': ideal_temp,
            'ideal_rainfall': ideal_rainfall,
            'duration_days': duration_days,
            'key_states': key_states,
            'why_message': why_message,
            'agronomic_tip': agronomic_tip,
            'match_grade': grade_text,
            'badge_class': grade_class,
        })

    return results

