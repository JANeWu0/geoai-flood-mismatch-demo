"""Template for the real geospatial workflow described in the thesis.

Optional dependencies:
    pip install -r requirements-geospatial.txt

Expected inputs:
- Copernicus EMS inundation polygons (authoritative event footprint)
- original 5 km thesis grid and separate 1 km refinement grid
- OpenStreetMap building footprints
- OpenStreetMap road/rail segments
- population layer
- geocoded and semantically filtered X-post points

The script intentionally contains no hard-coded download URLs or credentials.
"""
from __future__ import annotations


def required_overlay_outputs() -> list[str]:
    return [
        "grid_id",
        "inundation_ratio",
        "inundated_building_ratio",
        "road_disruption_ratio",
        "population",
        "response_signal_count",
    ]


if __name__ == "__main__":
    print(
        "Prepare separate 5 km thesis and 1 km refinement grid CSVs "
        "with these fields:"
    )
    print("\n".join(required_overlay_outputs()))
