from __future__ import annotations
from collections.abc import Sequence
import numpy as np
import pandas as pd

IMPACT_COMPONENTS = (
    "inundation_ratio",
    "inundated_building_ratio",
    "road_disruption_ratio",
)

def validate_weights(weights: Sequence[float]) -> np.ndarray:
    arr = np.asarray(weights, dtype=float)
    if arr.shape != (3,):
        raise ValueError("Exactly three weights are required.")
    if (arr < 0).any():
        raise ValueError("Weights must be non-negative.")
    if not np.isclose(arr.sum(), 1.0):
        raise ValueError("Weights must sum to 1.")
    return arr

def compute_impact_intensity(
    df: pd.DataFrame,
    weights: Sequence[float] = (1/3, 1/3, 1/3),
) -> pd.DataFrame:
    """Build I_i from the three thesis-defined physical-impact ratios.

    Equal weights are used as the transparent baseline because the thesis states
    that no defensible calibration data were available. Results are conditional
    on this modelling choice.
    """
    out = df.copy()
    w = validate_weights(weights)
    out["impact_intensity_raw"] = sum(
        weight * pd.to_numeric(out[col], errors="raise")
        for weight, col in zip(w, IMPACT_COMPONENTS)
    )
    out["impact_intensity_log"] = np.log1p(out["impact_intensity_raw"])
    return out

def weight_sensitivity(
    df: pd.DataFrame,
    schemes: dict[str, Sequence[float]],
) -> pd.DataFrame:
    frames = []
    for name, weights in schemes.items():
        result = compute_impact_intensity(df, weights)
        frames.append(pd.DataFrame({
            "grid_id": result["grid_id"],
            "scheme": name,
            "impact_intensity_raw": result["impact_intensity_raw"],
        }))
    return pd.concat(frames, ignore_index=True)
