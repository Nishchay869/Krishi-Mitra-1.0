# Local mandi prices

`/market/` displays official data.gov.in observations, with state, district, mandi and crop filters. Saved profile location/crops provide defaults. `/market/overview/` and `/market/api/` retain the separate state-average service.

## Configuration

Set `DATA_GOV_IN_API_KEY` in the project's `.env`, then restart Django. `.env.example` documents the variable. The key stays server-side; provider errors are sanitized to avoid leaking credential-bearing URLs.

Each price card prominently shows the commodity, variety, grade and report date. “Verify source report” exposes the original INR/quintal minimum, modal and maximum values and a source link. KG conversion preserves the originals and divides by exactly 100 using Decimal. The page distinguishes wholesale dated observations from retail or guaranteed current offers.

The Channapatna audit on 29 October 2026 fetched a Tomato / Local report dated 29 October: min 1,500, modal 2,500, max 3,000 INR/quintal. Google-indexed third-party pages showed different reporting dates (23 or 27 October), so prices must be compared on the same date and unit rather than overwritten to match a search snippet. These audit figures describe that specific fetched report, not a permanent fixture.

`provider.py` calls the official current daily mandi-price resource:
`https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`.

## Behavior

- Queries use provider state and commodity names, not Agmarknet numeric IDs.
- The local Agmarknet catalog supplies dropdown metadata. Provider-only district/market names are added when returned. Exact normalized matches and a small explicit city-name alias list prevent substituting a different location.
- When the saved district has no observations on the default view, show reporting markets across the state with a visible notice and their actual district labels. Explicit district/mandi filters remain strict; an empty selection offers a link to statewide reported markets.
- Only actual observations become price cards. A selected mandi without observations shows no data; state averages are never substituted.
- Minimum, modal and maximum values remain separate. QTL → KG divides each by 100 using Decimal. Missing values remain dashes.
- Every card shows its own reported date, variety and grade. Older observations display their age. Multiple varieties are not averaged together.
- Future report dates, explicitly incompatible price units, whitespace-only market/district names, malformed, nonfinite, negative, inverted-range and wrong-state/crop records are rejected or invalid price fields withheld. Conflicting prices for the same market/variety/grade/date are withheld with a notice unless a newer unambiguous report exists. An invalid explicit crop never silently substitutes Tomato. Latest records are retained per market/variety/grade.
- Results cache for 5 minutes and retain the actual source-fetch timestamp, separately from each observation’s report date. Requests are bounded to five 200-record pages with a 30-second overall request budget. A limited-results notice appears if pagination is truncated.
- Provider failures show an error, not fabricated prices. Without a key, setup-mode cards contain only catalog names and dashes.
- Mapped markets link to published coordinates; unmapped markets retain a named Maps search.

## Nearby markets and favourites

- The distance sheet offers all distances or 50/100/200/500 km, with counts for the current crop, state, district/mandi and favourite filters. Counts deduplicate market identities across varieties. The default is all distances so a sparse feed still displays available prices.
- Distances are approximate great-circle distances from the saved village point (the existing weather village resolver), or the device point supplied after clicking Use my location. They are explicitly labelled straight-line, not road distance. Radius filtering excludes unmapped markets; the page discloses the count excluded. Unknown locations never become zero-distance markets.
- `data/coordinates.json` contains 1,992 published market locations: a bounded 150,000-observation extract from India Data Portal's Agmarknet-derived APMC new-source CSV, plus the old-source Doddaballa Pur record with its individual source URL. Both source URLs are recorded in the file. These are location metadata, not current prices. Name, state and district must match the price observation after existing normalization; conflicting points are rejected. The snapshot is not a complete directory of every Indian market.
- Device coordinates are accepted only on a CSRF-protected POST and expire after one hour. The browser calls BigDataCloud's client-only reverse-geocoding endpoint after the user clicks, to display a place name; no coordinates are printed in the UI. If name lookup fails, the label is Your current location. The page explains the sharing and one-hour duration. Denial/errors preserve previous settings and prices. Device location does not silently change the selected state.
- Sorting supports nearest first, modal price high/low, and latest published. Nearest/highest labels and the highlight are derived from visible price reports; no price-change or historical trend is invented.
- Favourites are stored per account in `MarketFavourite`, keyed by normalized state/district/market; add/remove is idempotent, requires a signed market token and CSRF, and supports ordinary form POST as well as the enhanced star control. The favourite view respects current crop/location filters. Apply `python manage.py migrate` when deploying.
- API documentation and sources: [India Data Portal APMC dataset](https://ckandev.indiadataportal.com/dataset/agriculture-marketing), [BigDataCloud client geocoding](https://www.bigdatacloud.com/docs/free-api/free-reverse-geocode-to-city-api).

The source publishes daily observations, not tick-by-tick trading quotes. Availability depends on mandi reporting. Catalog crop names not recognized by the provider may have no records; mappings should be verified against real provider data before adding aliases.

Tests: `python manage.py test market accounts.test_localization --noinput`.
