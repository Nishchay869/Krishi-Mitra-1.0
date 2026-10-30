# Crop library

Public routes: `/crops/library/` and `/crops/library/<slug>/`.
The existing navigation links to the library for both guests and signed-in users.

`data/library.json` contains profiles for all 70 onboarding crops. Names, category
membership and local WebP photos come from `accounts/onboarding.py`. Search
matches English names and the current translated names; category and search
filters work together without JavaScript.

Profiles contain climate, exposure, annual rainfall where available, humidity,
watering characteristics, propagation, cultivation practices, soil texture,
drainage, pH where available, source links and documented companion crops.
Photos retain their existing attribution in `static/images/crops/credits.html`.

## Research and interpretation

All 70 profiles were expanded on 29 October 2026. Each has temperature guidance,
annual rainfall or water-management guidance, humidity guidance, pH and a planting
relationship or layout. User-facing unknown-source placeholders were removed by
adding content, rather than concealing empty fields.

`library_references.json` records the optimal temperature, annual rainfall and pH
ranges extracted from 65 species records on FAO's official EcoCrop site, with
record IDs, URLs and access dates. These are historical ecological envelopes, not
current local prescriptions. The site identifies them as ecological references;
do not reinterpret them as daily forecast targets, seasonal rainfall totals or
irrigation doses. Scientific names make the species mapping visible. Coffee
(Arabica/Robusta) and rapeseed/mustard keep separate species ranges.

Matching flower records absent from EcoCrop use TNAU, NHB and university extension
guides. Banana retains the Indian guides. Jasmine and tropical hibiscus use
qualitative temperature guidance instead of inventing numerical bounds. Rose's
range summarizes the guide's night/day temperatures. Four terrestrial flower
profiles describe supplemental irrigation instead of an unsupported annual rain
target; lotus explains pond-water management instead of a rainfall requirement.

Air humidity is not interchangeable with leaf wetness. Where no crop-specific RH
percentage was established, the page displays **Humidity guidance**, citing
UW–Madison's general airflow/leaf-wetness advice. Banana's published RH percentage
remains numeric. Qualitative humid/dry preferences retain their crop references.
No RH percentages were fabricated.

`field_sources` places citations beside temperature, rainfall, humidity, pH and
planting-relationship guidance. Cultivation and soil-texture descriptions remain
introductory summaries; growers should use the regional guide for timing and
rates. Photos are species examples, not guarantees of the cultivar represented
by a guide. Drought tolerance does not imply irrigation is unnecessary for yield.

The 65 profiles with photo links distinguish documented intercrops, rotations and
general habitat strips. Rice and ragi show sequential rotation, not simultaneous
planting. Coriander habitat strips are explicitly general insect-habitat design,
not a crop-specific pest-control guarantee. Five flower profiles use dedicated
bed/pond layouts instead of asserting an unsubstantiated companion pairing.
Young-orchard, fodder and climbing-bean constraints are shown where relevant.
Coconut canopy age and separate water/nutrient requirements still require the
linked regional guide. Source suggestions are not universal pest-control claims.

## Runtime and localization

No model, weather, translation, or other external API is called by these views.
The HTML is server-rendered; images and CSS are local. Source links are optional
external references. This does not add offline HTML caching: opening a library
page still requires access to the application server.

Reusable terms are bundled in the existing English and 15 native-language
catalogs. Edit `locale/ui/*.json`, then run `python scripts/build_translations.py`.
For content updates, restart a server running with `--noreload` because the catalog
is cached in memory. Linguistic and regional agronomy review remain useful before
relying on these summaries as production-specific advice.

Validation: `python manage.py test crops.test_library accounts.test_localization --noinput`.
