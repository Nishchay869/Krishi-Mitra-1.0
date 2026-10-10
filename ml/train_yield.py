"""Train the crop yield regression model (spec §3.4).

Dataset: Kaggle "Crop Yield in Indian States" (state-level, 1997-2020), data/crop_yield.csv.
Its Fertilizer/Pesticide columns are one national per-hectare rate per year multiplied by
area, so they carry no field-level information and are not used as features.

Usage: python -m ml.train_yield
Compares Random Forest, Linear and Decision Tree regression (MSE, RMSE, R²) on a random
80/20 split and on a time split (train <= 2015, test 2016-2020), then saves Random Forest
retrained on all data to ml/models/yield_rf.joblib.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / 'data' / 'crop_yield.csv'
MODEL_PATH = BASE_DIR / 'ml' / 'models' / 'yield_rf.joblib'
CATEGORICAL = ['Crop', 'Season', 'State']
NUMERIC = ['Annual_Rainfall', 'Crop_Year']
FEATURES = CATEGORICAL + NUMERIC
# Coconut is recorded in nuts/ha and "Oilseeds total" is an aggregate of other rows.
EXCLUDED_CROPS = {'Coconut', 'Oilseeds total'}
BALE_CROPS = {'Cotton(lint)': 'bales (170 kg)/ha', 'Jute': 'bales (180 kg)/ha', 'Mesta': 'bales (180 kg)/ha'}


def drop_outliers(df, k=3.0):
    """Drop per-crop extreme yields (e.g. maize at 990 t/ha), which are data-entry errors."""
    log_y = np.log(df.Yield)
    grouped = log_y.groupby(df.Crop)
    q1, q3 = grouped.transform('quantile', 0.25), grouped.transform('quantile', 0.75)
    iqr = q3 - q1
    return df[(log_y >= q1 - k * iqr) & (log_y <= q3 + k * iqr)]


def load(path=CSV_PATH):
    df = pd.read_csv(path)
    for col in CATEGORICAL:
        df[col] = df[col].str.strip()
    df = df[(df.Yield > 0) & ~df.Crop.isin(EXCLUDED_CROPS)]
    return drop_outliers(df).reset_index(drop=True)


def make_model(regressor):
    pre = ColumnTransformer([('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL)], remainder='passthrough')
    # Yields span 0.05-80 t/ha across crops; fitting log(yield) keeps small-yield crops from being ignored.
    return TransformedTargetRegressor(make_pipeline(pre, regressor), func=np.log1p, inverse_func=np.expm1)


def candidates():
    return {
        'random_forest': make_model(RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=-1)),
        'linear_regression': make_model(LinearRegression()),
        'decision_tree': make_model(DecisionTreeRegressor(min_samples_leaf=3, random_state=42)),
    }


def evaluate(model, X_train, X_test, y_train, y_test):
    pred = model.fit(X_train, y_train).predict(X_test)
    mse = mean_squared_error(y_test, pred)
    return {'mse': round(mse, 3), 'rmse': round(float(np.sqrt(mse)), 3), 'r2': round(r2_score(y_test, pred), 4),
            'r2_log': round(r2_score(np.log1p(y_test), np.log1p(pred)), 4)}


def main():
    df = load()
    X, y = df[FEATURES], df['Yield']
    print(f'{len(df)} rows, {df.Crop.nunique()} crops, {df.State.nunique()} states')

    splits = {
        'random_80_20': train_test_split(X, y, test_size=0.2, random_state=42),
        'time_2016_2020': (X[df.Crop_Year <= 2015], X[df.Crop_Year > 2015], y[df.Crop_Year <= 2015], y[df.Crop_Year > 2015]),
    }
    metrics = {}
    for split_name, split in splits.items():
        print(f'\n{split_name}:')
        for name, model in candidates().items():
            m = metrics.setdefault(split_name, {})[name] = evaluate(model, *split)
            print(f"  {name:>18}: RMSE {m['rmse']:7.3f}  MSE {m['mse']:9.3f}  R² {m['r2']:.4f}  (R² log-scale {m['r2_log']:.4f})")

    final = candidates()['random_forest'].fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        'model': final, 'features': FEATURES, 'latest_year': int(df.Crop_Year.max()),
        'crops': sorted(df.Crop.unique()), 'states': sorted(df.State.unique()), 'seasons': sorted(df.Season.unique()),
        'crop_seasons': {c: sorted(g.Season.unique()) for c, g in df.groupby('Crop')},
        'units': BALE_CROPS, 'metrics': metrics,
        # Median yield over the last 5 recorded years per crop/state, shown to farmers for comparison.
        'history': {f'{c}|{st}': round(float(g[g.Crop_Year > g.Crop_Year.max() - 5].Yield.median()), 3)
                    for (c, st), g in df.groupby(['Crop', 'State'])},
    }, MODEL_PATH)
    (MODEL_PATH.parent / 'yield_metrics.json').write_text(json.dumps(metrics, indent=2))
    print(f'\nSaved Random Forest to {MODEL_PATH}')


if __name__ == '__main__':
    main()
