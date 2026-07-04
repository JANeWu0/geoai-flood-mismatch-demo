# Data Card

## Dataset status

The files in `data/` are **synthetic demo data** created to match the thesis narrative and demonstrate the method.

They are not official disaster records and should not be used as evidence of real resource allocation without replacement by verified data.

## Files

- `sample_municipalities.csv`: municipality-level demo table.
- `sample_municipalities.geojson`: point GeoJSON version for map use.
- `sample_social_posts.csv`: tiny synthetic text sample for response-signal classification.

## Recommended real sources for a production version

- Copernicus EMS flood extent layers;
- Sentinel-1 / Sentinel-2 imagery;
- OpenStreetMap building and road layers;
- Italian Civil Protection bulletins;
- regional/municipal evacuation and pump deployment reports;
- properly anonymized and ethically collected social-media or crowdsourced crisis reports.

## Ethics notes

- Do not publish raw personal social-media posts if they contain names, handles, addresses, or distress details.
- Aggregate to municipality/grid level.
- Document bias: areas with older populations or lower internet access may be underrepresented in social data.
