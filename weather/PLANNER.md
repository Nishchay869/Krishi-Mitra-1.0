# Saved-crop weather planner

`/weather/` uses `Profile.selected_crops` from signup/profile, `growing_place`, the saved village, and the existing OpenWeather five-day / three-hour forecast. The user can override the location and report soil as dry, moist or wet. No LLM, translation API, notification subscription or new paid API is invoked.

The UI shows the next forecast (not a current observation), forecast dates, the first candidate time for each saved crop, and scrollable spraying/irrigation timelines. Timestamps use the provider's location offset. Past entries are removed. Localized strings are bundled in the existing 16 complete catalogs.

## Screening rules

These conservative application heuristics are not experimentally validated crop prescriptions or pesticide-label limits:

- A spray candidate needs three consecutive three-hour entries covering the next six hours, no precipitation, rain probability below 30%, daylight, local time 08:00–17:00, temperature 10–28°C, humidity 40–85%, wind 1.5–3.3 m/s and available gust values no higher than 4.5 m/s. Fog, storms, night-time, calm wind and missing data never earn a candidate.
- Candidate status is **Check conditions**, never **safe** or **optimal**. Forecasts cannot establish on-site wind direction, temperature inversions, leaf wetness, pollinator activity or product-specific rainfastness. The product label and an on-site check control the decision. Six hours is a forecast-screening horizon, not a universal rainfast interval.
- Irrigation weather screening prefers 06:00–11:00 or 16:00–19:00 and avoids forecast rain, high heat, frost and reported wet soil. Unknown or moist soil always requires a soil check. The planner does not prescribe quantities, durations or use universal volumetric-water-content thresholds.
- Paddy rice receives a water-level reminder rather than generic irrigation dates. Containers receive drainage guidance. Other crops receive a root-zone moisture reminder. Stage, variety, soil texture and irrigation system are not collected, so the UI does not claim fully crop-specific water requirements. A future-stage soil observation is not assumed to remain true: every candidate requires field confirmation.

The legacy `/weather/api/` retains its original advisory response for compatibility; the new website planner uses `planner.py`. Changes to its historical VWC-based advice are outside this UI change.

References:
- https://extension.umn.edu/agriculture/crop-production/weed-management/avoiding-herbicide-drift
- https://extension.umn.edu/agriculture/specialty-crops/vegetable-farming/irrigation-strategies-for-vegetables
- https://www.montana.edu/extension/pesticides/reference/drift.html

The spraying timeline opens an accessible details dialog with selectable forecast slots and the individual screening checks. Its temperature/humidity chart plots the selected forecast against the existing screening band; it is not a Delta-T calculation or a standalone spraying recommendation. The dialog uses bundled JavaScript and translations, without additional API calls.

Tests: `python manage.py test weather accounts.test_localization --noinput`.


## Village forecast location

The planner defaults to `Profile.village`, qualified by district/state in the
visible label. OpenWeather direct geocoding resolves the village within India
and checks its state, then the forecast request uses `lat`/`lon` rather than the
district name. Missing villages prompt a profile update instead of silently
loading district weather. The district is retained as context/cache identity;
OpenWeather does not expose district boundaries, so distant same-state village
matches are rejected instead of guessed. Duplicate boundary/locality records
within a two-kilometre cluster are combined into one village-area point. A
verified spelling mapping supports Hunasamaranalli → Hunasamaranahalli in
Karnataka, without changing the saved profile spelling. Local-name aliases and common state-name
aliases are supported. Native-script vowel marks are preserved when comparing
names. Unknown or ambiguous villages show the existing location error without a
district fallback.

Users can override the saved place. `Village, district, state` inputs use the same
village resolver; a single manually entered town retains the legacy name lookup.
Resolved public village coordinates are cached for a day, with coordinate-based
forecast responses cached for 30 minutes. Returned provider town names never
replace the requested village label. Forecasts describe the village area, not
measurements from a weather station in each field. The legacy weather API remains
compatible with its existing explicit location parameter.

References: [OpenWeather geocoding](https://openweathermap.org/api/geocoding-api)
and [coordinate-based five-day forecast](https://openweathermap.org/api/forecast5).
Regression coverage: `python manage.py test weather.test_village weather.test_planner`.
