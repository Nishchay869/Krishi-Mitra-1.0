# Crop selector images

70 local WebP images are used by the farmer preference picker. Canonical crop names and category membership live in `accounts/onboarding.py`.

`credits.json` records the source, author, license, and modifications for every asset. `credits.html` exposes these credits from the crop picker. Each image retains its individual source license; the included `gfdl-1.2.txt` applies to the image marked GFDL 1.2.

Images are resized to at most 320 pixels and loaded lazily. No image search, translation, or generation API runs when farmers use the picker.

This catalog records farmer preferences. Adding a crop here does not extend the disease or yield models' supported classes.
