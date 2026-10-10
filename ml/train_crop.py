"""Train the crop recommendation model (spec §3.3).

Usage: python -m ml.train_crop [--csv data/crop_recommendation.csv]
Compares Random Forest against Decision Tree and SVM, then saves the Random Forest
pipeline to ml/models/crop_rf.joblib.
"""
import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent.parent
FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
MODEL_PATH = BASE_DIR / 'ml' / 'models' / 'crop_rf.joblib'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default=BASE_DIR / 'data' / 'crop_recommendation.csv')
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    X, y = df[FEATURES], df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    candidates = {
        'random_forest': RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        'decision_tree': DecisionTreeClassifier(random_state=42),
        'svm': make_pipeline(StandardScaler(), SVC(random_state=42)),
    }
    scores = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        scores[name] = accuracy_score(y_test, model.predict(X_test))
        print(f'{name:>14}: accuracy {scores[name]:.4f}')

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': candidates['random_forest'], 'features': FEATURES, 'accuracy': scores['random_forest']},
                MODEL_PATH)
    (MODEL_PATH.parent / 'crop_metrics.json').write_text(json.dumps(scores, indent=2))
    print(f'Saved Random Forest to {MODEL_PATH}')


if __name__ == '__main__':
    main()
