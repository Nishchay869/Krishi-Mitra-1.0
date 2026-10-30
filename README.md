# Krishi Mitra — AI-Powered Agriculture Assistant (MVP)

Django web app for smallholder farmers, implementing the MVP scope of [spec.md](spec.md):

| Module | Implementation | Status |
|---|---|---|
| Conversational assistant | TF-IDF retrieval over a curated, source-tagged knowledge base (spec §3.1 Option B) | Working |
| Crop recommendation | Random Forest on the Kaggle Crop Recommendation dataset (N, P, K, temp, humidity, pH, rainfall) | Working (99.5% test accuracy) |
| Yield prediction | Random Forest regression on Kaggle "Crop Yield in Indian States" (crop, season, state, rainfall); compared with Linear and Decision Tree regression | Working (R² 0.83 on unseen 2016–2020 data) |
| Leaf assessment | Google Gemini image analysis with crop context and structured control guidance | Requires server-side Gemini API key; no measured field-accuracy claim |
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

## Disease Check with Gemini

Add a server-side key to `.env` and restart Django:

```dotenv
GEMINI_API_KEY=your-key-here
GEMINI_DISEASE_MODEL=gemini-3.8-flash
```

Disease Check sends the uploaded leaf photo and optional crop/location/observation fields to Google's Interactions API. The server normalizes orientation, removes metadata, converts to JPEG, and preserves detail up to a 2048px longest edge. Images remain subject to the existing 5 MB upload limit and a 25-megapixel processing limit. The API key stays in a request header on the server; the browser never receives it. `store=false` disables stored interaction state; Google's applicable API data-use policies still apply. No image upload is saved locally by this feature.

The structured result explains visible observations, possible causes, non-chemical control, prevention, follow-up, and candidate active ingredients only when the assessment supports them. Chemical candidates are AI suggestions for local verification, not confirmed registrations or prescriptions. Unclear/non-leaf images, crop conflicts, low certainty, and healthy assessments do not receive chemical options. The app does not invent confidence percentages or spray doses; users must confirm a product's current crop/target label, application requirements, and harvest interval. Similar symptoms may have different causes. Gemini does not guarantee diagnostic accuracy.

Results retain `plant`, `disease`, `treatment`, and `is_healthy` for existing dashboards. `certainty` is qualitative and self-assessed; the old CNN `confidence` percentage is deliberately absent. Service errors identify configuration/access/quota/timeout issues without exposing provider credentials. The existing API and browser submissions are limited to six requests per minute per user/IP using Django cache; use a shared cache for consistent limits across production workers.

The legacy CNN artifacts and `ml.train_disease` script remain available for separate research, but Disease Check does not load TensorFlow or use the local model as a fallback.

References: [Gemini Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview), [structured outputs](https://ai.google.dev/gemini-api/docs/structured-output), and [Government of India guidance on pesticide labels](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2146917&lang=2&reg=48).

## REST endpoints

| Method | URL | Body / params |
|---|---|---|
| POST | `/chat/api/` | `{"message": "..."}` → `reply`, `intent`, `confidence`, `source`, `source_url` |
| POST | `/crops/api/` | `{"N","P","K","temperature","humidity","ph","rainfall"}` → top-3 crops |
| POST | `/crops/yield/api/` | `{"crop","season","state","rainfall","area_ha"?}` → yield/ha, likely range, total, unit |
| POST | `/disease/api/` | multipart `image`, optional `crop`, `location`, `notes` → structured Gemini assessment, qualitative certainty, control measures, and conditional chemical candidates |
| GET | `/market/api/?state=16` | latest prices, previous-day prices, change, % and direction (omit `state` for all-India) |
| GET | `/weather/api/?location=Mandya&soil_moisture=20` | forecast + advisories |

POST endpoints require Django's CSRF token (`X-CSRFToken` header).

## Knowledge base & fairness

Chatbot answers come only from `KnowledgeEntry` rows, each with a `source` and `source_url` shown to the user (spec §4.3 provenance). Administrators extend the knowledge base in Django admin; the admin dashboard lists unanswered questions to show gaps.

## React Bits UI (React islands)

Most pages are Django templates + Bootstrap. Animated React Bits components are added as
"islands": `frontend/` is a Vite + React + Tailwind project whose build goes to
`static/frontend/islands.{js,css}`; a template mounts a component with
`<div data-react-island="HomeHero" data-props='{...}'>` (see `templates/home.html`).
Tailwind is loaded **without its preflight reset** so it never restyles Bootstrap pages.

```bash
cd frontend
npm install
npx shadcn@latest add @react-bits/<Component>-TS-TW   # e.g. SplitText-TS-TW
npm run dev     # preview islands at http://localhost:5173
npm run build   # rebuild static/frontend/ for Django (commit the output)
```

New islands go in `frontend/src/islands/` and are registered (lazy-loaded) in `frontend/src/islands.tsx`.
Current islands: `HomeHero` (SplitText + RotatingText) and `LiveStrands` (Strands background of the live
voice conversation, driven by `krishi:live` events from `static/js/chat.js`).

**Claude Code + MCP:** `.mcp.json` (project root) starts the shadcn MCP server inside `frontend/`,
so Claude can search and install React Bits components by name. Restart Claude Code and run
`/mcp` to approve/check the `shadcn` server.

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

## UI and motion

The shared UI in `static/css/app.css` styles every Django page. The homepage uses a
procedural Three.js wheat scene, GSAP entrance effects, and Locomotive Scroll 5 for
smooth desktop wheel scrolling. `frontend/src/experience.ts` coordinates progressive
enhancement; `farm-scene.ts` owns WebGL resources and disposal.

- Forms, navigation and content are server rendered and work without these bundles.
- Reduced motion and Save-Data skip animation. Touch and narrow screens keep native
  scrolling and an inline vector landscape instead of downloading Three.js.
- The 3D scene uses three instanced draw calls, a 1.5 pixel-ratio cap, and a 30fps
  animation cap; rendering pauses outside the viewport or while the tab is hidden.
- React and the voice visualizer load on demand. Mobile and reduced motion retain
  voice controls without the WebGL voice background.
- Run `npm ci && npm run build` in `frontend/` after source changes. Generated assets
  belong in `static/frontend/`. The shared build runtime has its own hashed chunk to
  prevent duplicate entry execution through cache-busted imports.

Validation: Django's test suite plus Chromium checks at 320, 390, 768 and 1440px for
page rendering, horizontal overflow, mobile navigation and JavaScript errors. These
are responsive browser checks, not a guarantee of performance on every physical device.

## Farmer language preferences

Signup and profile language preferences apply to the complete server-rendered UI,
form labels/help/validation, result labels, weather advisories and chat controls.
The saved profile overrides browser preferences. Updating a profile applies the new
language immediately; the language cookie also preserves it on public pages after logout.

The registry in `accounts/languages.py` covers the 22 scheduled Indian languages plus
English. Completed bundled catalogs: English, Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi,
Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri, Marathi, Tamil, and Telugu. Other languages remain unavailable in signup until their entire catalog
is generated and compiled. Text translation coverage is separate from voice coverage;
voice controls appear only for languages supported by the configured speech service.

Translations live in `locale/ui/<code>.json`; English is the source inventory. Rebuild
compiled `.po`/`.mo` catalogs with `python scripts/build_translations.py` (requires GNU
gettext's `msgfmt`). Both source and compiled catalogs belong in version control; page
requests never call an external service to translate the interface. Restart Django after
changing catalogs. Run `python manage.py test accounts.test_localization` to check coverage,
profile persistence, cross-page language selection, source data preservation and validation.

UI language catalogs are generated without API credits. For an offline rebuild on Apple Silicon:

```bash
uv venv .venv-translate
uv pip install --python .venv-translate/bin/python -r requirements-translate.txt
# One-time model download (free, approximately 2.4 GB):
.venv-translate/bin/hf download mlx-community/sarvam-translate-mlx-4bit \
  --revision 7c664b5203a0db7f6d1e8a0c0a2a0d76c8f41e64 \
  --local-dir .offline-models/sarvam-translate-4bit
python manage.py translate_ui --status
python manage.py translate_ui  # local model only; internet explicitly disabled
```

The quantized model derives from [Sarvam Translate](https://huggingface.co/sarvamai/sarvam-translate).
The pinned [MLX conversion](https://huggingface.co/mlx-community/sarvam-translate-mlx-4bit)
is used only during generation. No model weights or MLX runtime are sent to farmers' devices;
production servers need only the bundled JSON/gettext catalogs. Generation saves resumable
drafts and rejects altered placeholders, changed numbers, repetitions and truncated outputs.
Review machine translations, especially agricultural treatment wording, before production.
No translation API credentials or credits are used by this build process.

CSS, scripts and icon fonts are served locally. A service worker saves only public assets and
language packs; it never caches account/profile pages, chat histories, uploads or API responses.
After one successful online visit, offline navigation opens a translated reference screen and
allows changing among all installed language packs. Account forms, new predictions and live
services still require the Django server. Running Django locally allows its local models/forms
to work without internet; weather, current market prices, cloud chat translation and voice
still require their respective services. First-ever installation needs connectivity.

Odia uses Django's `or` code and Sarvam's `od-IN` code. Kashmiri, Sindhi and Urdu use RTL
layout when enabled. This is scheduled-language coverage, not every Indian dialect.

## Fertilizer calculation

Open Crop Advisor → Fertilizer Calculator (`/crops/fertilizer/`, login required).
The selector has **54 crop types / 62 presets** in eight categories: vegetables,
cereals, pulses, fruits, oilseeds, spices, cash crops and flowers. Available saved
crops are selected initially. Crop choice preloads recommended **application
rates** of N, P₂O₅ and K₂O; Edit allows a soil-test recommendation to override them.
These are not measured soil nutrient levels.

Field crops ask for field size in acres, hectares or gunta (40 gunta = 1 acre).
True trees ask for count, with age-specific or explicitly bearing-tree presets.
A per-plant source (for example Rose, Jasmine or Banana) asks for both field size
and actual plant count; area never implies a planting density. Pumpkin's source
uses grams per pit, so it asks for pit count and labels all quantities per pit.
Papaya's preset is explicitly one repeated application, not an annual total.

`crops/fertilizer_presets.py` records each crop's rates, source, scope, units and
available stage fractions. References come from TNAU crop guides and Vikaspedia;
the source and applicable region/regime are shown on the page. Regional defaults
do not replace a local soil-test recommendation. They exclude organic amendments
and other nutrients. Where a source does not establish timing, the detail page
links the source instead of inventing an application schedule.

Results offer **MOP/TSP/Urea** and **DAP/MOP/Urea**. Grades are MOP 0–0–60,
TSP 0–46–0, urea 46–0–0 and DAP 18–46–0. DAP nitrogen is credited before
calculating urea. Cards show kilograms and fractional bag equivalents (45 kg
urea, 50 kg other products). Check actual grades and pack sizes; weigh the dose
instead of rounding application amounts to whole bags.

**See application** opens a separate page with crop reference stages and product
masses. Stage totals conserve the season/annual/application totals before display
rounding. Edited rates require a locally confirmed split. A combination that
cannot match a stage's nitrogen target does not receive an invented schedule.
Cucumber's source uses drip fertigation and different soluble fertilizers: its
conversion is labelled as nutrient equivalents, not a drip-injection recipe.
Granular TSP must not be injected into drip equipment.

Relevant products use locally served **real bag photos** with multiple branded
alternatives: SPIC and Jai Kisaan MOP, SPIC/IFFCO/Jai Kisaan DAP, SPIC/IFFCO
neem-coated urea, and Jai Kisaan Navratna TSP. All alternatives match the standard
grade used by the calculator; adding a brand does not change nutrient quantities. Source links
appear on each card; original URLs, owners, access dates and image hashes are in
`static/images/fertilizers/credits.json`. They are packaging examples, not stock
or price listings. Product category filters work with JavaScript; all cards are
available without it.

Nearby shop searches use the saved village/district/state, an edited location or
an explicit **Use my location** action. They open live Google Maps searches;
shop addresses, stock, prices and distances are not fabricated. Searches from a
product card include its brand name. Maps URLs need no API key. Phone location
is requested only after a click, then resolved into locality, city, state and
postcode using BigDataCloud’s browser-only reverse-geocoding API. The location
field shows the place name rather than latitude/longitude. Lookup errors, IP-only
results and denied permission preserve the previous place and allow manual entry.
Coordinates are sent directly to BigDataCloud only for this user action and are
not written to the profile. The UI explains this data use and links the provider. The location form also works without JavaScript. Call the shop to
confirm stock before travelling.

Signed detail links preserve inputs for 24 hours and are restricted to the same
signed-in user. Back navigation restores the crop, area/count and calculation
without a repeat POST. Calculations are not stored in the database. UI text uses
the bundled catalogs, without a translation API call on page loads.

References: [IFDC nutrient conversion, p.27](https://ifdc.org/wp-content/uploads/2023/04/West-Africa-Fertilizer-Bulk-Blending-Manual-November-2022-Edition.pdf),
[TSP 0–46–0](https://www.ocpna.com/product/duraphos-0-46-0/),
[Maps search URLs](https://developers.google.com/maps/documentation/urls/get-started).

Tests: `python manage.py test crops.test_fertilizer crops.test_fertilizer_application crops.test_fertilizer_products`.

Place-name lookup reference: [BigDataCloud client reverse geocoding](https://www.bigdatacloud.com/docs/free-api/free-reverse-geocode-to-city-api). Calls use the current browser geolocation only; the free client endpoint is never called by the server or for batch lookups.
