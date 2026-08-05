"""Template for the real geospatial workflow described in the thesis.

Optional dependencies:
    pip install -r requirements-geospatial.txt

Expected inputs:
- Copernicus EMS inundation polygons (authoritative event footprint)
- 1 km analysis grid
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
    print("Prepare a 1 km grid CSV with these fields:")
    print("\n".join(required_overlay_outputs()))
