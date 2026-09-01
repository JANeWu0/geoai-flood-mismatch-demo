# Replacing the Demo with the Original Research Data

## Physical-impact stream

To reproduce the source record, first prepare the original 5 km grid. To run
the post-thesis sensitivity comparison, prepare a separate 1 km grid. For
every cell at each resolution, calculate:

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

Do not mix the two resolutions in one attribute table or overwrite the 5 km
outputs with the 1 km run. Preserve resolution-specific cell IDs, intermediate
tables, class breaks and exported figures so that changes caused by spatial
support remain auditable.

## Diagnostics

Produce both:

- share-based `delta_share`, `smi_contribution` and overall `SMI`;
- `standardised_residual = z(log1p(I)) - z(log1p(R))`;
- `mismatch_magnitude = |SR|` rescaled to `[0, 1]`.

Do not interpret low visibility as proof that no operational response occurred. Cross-check high-mismatch cells with road disruption, official summaries and intervention layers.

When comparing resolutions, evaluate persistence of regional structures and
residual direction. Do not infer equality from matching colour shades because
aggregation, zero counts, standardisation and class intervals change with the
grid.
