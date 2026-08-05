# Replacing the Demo with the Original Research Data

## Physical-impact stream

Prepare a 1 km grid and calculate, for every cell:

- `inundation_ratio`: inundated area / cell area;
- `inundated_building_ratio`: inundated OSM buildings / all OSM buildings;
- `road_disruption_ratio`: inundated road and rail length / total road and rail length.

Use the Copernicus EMS Rapid Mapping flood delineation as the authoritative event footprint. Sentinel-1, Sentinel-2, orthophoto and LiDAR products can support inspection and cross-checking, but the final thesis uses the Copernicus footprint as the primary delineation.

## Visibility stream

For each post:

1. keep an auditable post ID and timestamp;
2. apply the fixed semantic categories;
3. preserve the place mention and geocoding cue;
4. remove duplicates in the event window;
5. aggregate retained response/demand signals to the same grid;
6. report absolute counts and a per-capita rate.

## Diagnostics

Produce both:

- share-based `delta_share`, `smi_contribution` and overall `SMI`;
- `standardised_residual = z(log1p(I)) - z(log1p(R))`;
- `mismatch_magnitude = |SR|` rescaled to `[0, 1]`.

Do not interpret low visibility as proof that no operational response occurred. Cross-check high-mismatch cells with road disruption, official summaries and intervention layers.
