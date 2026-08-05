from __future__ import annotations
from pathlib import Path
import pandas as pd

GRID_REQUIRED = {
    "grid_id", "municipality", "latitude", "longitude", "population",
    "inundation_ratio", "inundated_building_ratio",
    "road_disruption_ratio", "response_signal_count"
}

def load_grid(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = GRID_REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing grid columns: {sorted(missing)}")
    if not df["grid_id"].is_unique:
        raise ValueError("grid_id must be unique.")
    ratio_cols = [
        "inundation_ratio",
        "inundated_building_ratio",
        "road_disruption_ratio",
    ]
    for col in ratio_cols:
        if not df[col].between(0, 1).all():
            raise ValueError(f"{col} must lie in [0, 1].")
    if (df["population"] < 0).any() or (df["response_signal_count"] < 0).any():
        raise ValueError("Population and response counts must be non-negative.")
    return df
