from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class MismatchSummary:
    smi: float
    n_units: int

def _zscore(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="raise").astype(float)
    std = values.std(ddof=0)
    if np.isclose(std, 0.0):
        return pd.Series(np.zeros(len(values)), index=values.index)
    return (values - values.mean()) / std

def compute_mismatch(
    df: pd.DataFrame,
    impact_col: str = "impact_intensity_raw",
    visibility_col: str = "response_visibility_raw",
) -> tuple[pd.DataFrame, MismatchSummary]:
    """Compute the two complementary diagnostics defined in the thesis.

    1) Distributional SMI:
       Delta_i = R_share_i - I_share_i
       SMI_i = 0.5 * |Delta_i|
       SMI = sum(SMI_i)

    2) Directional standardised residual:
       SR_i = z(log(1 + I_i)) - z(log(1 + R_i))
       SR_i > 0: under-visibility relative to impact
       SR_i < 0: over-visibility relative to impact
    """
    out = df.copy()
    impact = pd.to_numeric(out[impact_col], errors="raise").clip(lower=0)
    visibility = pd.to_numeric(out[visibility_col], errors="raise").clip(lower=0)
    if impact.sum() <= 0 or visibility.sum() <= 0:
        raise ValueError("Impact and visibility totals must both be positive.")

    out["impact_share"] = impact / impact.sum()
    out["visibility_share"] = visibility / visibility.sum()
    out["delta_share"] = out["visibility_share"] - out["impact_share"]
    out["smi_contribution"] = 0.5 * out["delta_share"].abs()
    smi = float(out["smi_contribution"].sum())

    out["impact_z"] = _zscore(np.log1p(impact))
    out["visibility_z"] = _zscore(np.log1p(visibility))
    out["standardised_residual"] = out["impact_z"] - out["visibility_z"]

    abs_sr = out["standardised_residual"].abs()
    max_abs = abs_sr.max()
    out["mismatch_magnitude"] = 0.0 if np.isclose(max_abs, 0.0) else abs_sr / max_abs

    out["diagnostic_direction"] = np.select(
        [
            out["standardised_residual"] > 0.25,
            out["standardised_residual"] < -0.25,
        ],
        [
            "under_visibility",
            "over_visibility",
        ],
        default="approximate_balance",
    )
    return out, MismatchSummary(smi=smi, n_units=len(out))
