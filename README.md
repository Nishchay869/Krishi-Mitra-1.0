# Krishi Mitra — AI-Powered Agriculture Assistant (MVP)

Django web app for smallholder farmers, implementing the MVP scope of [spec.md](spec.md):

| Module | Implementation | Status |
|---|---|---|
| Conversational assistant | TF-IDF retrieval over a curated, source-tagged knowledge base (spec §3.1 Option B) | Working |
| Crop recommendation | Random Forest on the Kaggle Crop Recommendation dataset (N, P, K, temp, humidity, pH, rainfall) | Working (99.5% test accuracy) |
| Yield prediction | Random Forest regression on Kaggle "Crop Yield in Indian States" (crop, season, state, rainfall); compared with Linear and Decision Tree regression | Working (R² 0.83 on unseen 2016–2020 data) |
| Disease detection | 64×64 CNN, 3 conv + max-pool blocks, PlantVillage (38 classes, 54,305 images) | Working (94.6% validation accuracy) |
| Weather & advisory | OpenWeatherMap 5-day forecast + rule-based advisories + soil-moisture irrigation hint | Working once API key is set |
| Market prices | Daily mandi prices for 25 major crops (all-India or by state) from Agmarknet, compared with the previous reporting day (green ▲ / red ▼), with MSP | Working (live, no API key) |
| Accounts | Farmer / Administrator roles, farmer dashboard, admin dashboard, Django admin | Working |

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add OPENWEATHER_API_KEY
set -a; source .env; set +a

python -m ml.train_crop         # trains + saves ml/models/crop_rf.joblib
python -m ml.train_yield        # trains + saves ml/models/yield_rf.joblib
python manage.py migrate
python manage.py seed_knowledge # loads data/knowledge_base.json
python manage.py createsuperuser  # administrator account
python manage.py runserver
```

Open http://127.0.0.1:8000, register as a farmer, and try the features.

## Disease detection model

```bash
pip install -r requirements-ml.txt
# Download PlantVillage (e.g. Kaggle "PlantVillage dataset", color images) and arrange as:
#   data/plantvillage/<Plant___Disease>/*.jpg
python -m ml.train_disease --data data/plantvillage --epochs 15
```

This writes `ml/models/disease_cnn.keras` and `disease_classes.json`. Until then the Disease Check page shows a "model not trained" notice.

## REST endpoints

| Method | URL | Body / params |
|---|---|---|
| POST | `/chat/api/` | `{"message": "..."}` → `reply`, `intent`, `confidence`, `source`, `source_url` |
| POST | `/crops/api/` | `{"N","P","K","temperature","humidity","ph","rainfall"}` → top-3 crops |
| POST | `/crops/yield/api/` | `{"crop","season","state","rainfall","area_ha"?}` → yield/ha, likely range, total, unit |
| POST | `/disease/api/` | multipart `image` → plant, disease, treatment, confidence |
| GET | `/market/api/?state=16` | latest prices, previous-day prices, change, % and direction (omit `state` for all-India) |
| GET | `/weather/api/?location=Mandya&soil_moisture=20` | forecast + advisories |

POST endpoints require Django's CSRF token (`X-CSRFToken` header).

## Knowledge base & fairness

Chatbot answers come only from `KnowledgeEntry` rows, each with a `source` and `source_url` shown to the user (spec §4.3 provenance). Administrators extend the knowledge base in Django admin; the admin dashboard lists unanswered questions to show gaps.

## Tests

```bash
python manage.py test
```

## Yield model notes

The yield dataset is state-level (1997–2020), so estimates are regional averages rather than
field-specific predictions. Its Fertilizer/Pesticide columns are a single national per-hectare
rate per year, so they are not used as inputs. Coconut (recorded in nuts) and per-crop extreme
outliers are dropped. Cotton, jute and mesta yields are in bales/ha; everything else is tonnes/ha.
Metrics for all three algorithms are in `ml/models/yield_metrics.json`.

## Not yet implemented (Phase 2 per spec)

Field-level yield prediction from soil N-P-K (no public dataset links soil tests to yields), multilingual responses, Telegram/WhatsApp delivery, location-similarity recommendations, IoT sensor ingestion.
