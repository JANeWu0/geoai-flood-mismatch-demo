from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MismatchSummary:
    """Global summary for one executed dataset."""

    smi: float
    n_units: int


def _zscore(series: pd.Series) -> pd.Series:
    """Population z-score (ddof=0), matching the grid-surface standardisation."""

    values = pd.to_numeric(series, errors="raise").astype(float)
    std = values.std(ddof=0)
    if np.isclose(std, 0.0):
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return (values - values.mean()) / std


def _minmax(series: pd.Series) -> pd.Series:
    """Rescale a non-negative diagnostic surface to [0, 1]."""

    values = pd.to_numeric(series, errors="raise").astype(float)
    lower = float(values.min())
    upper = float(values.max())
    span = upper - lower
    if np.isclose(span, 0.0):
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return (values - lower) / span


def compute_mismatch(
    df: pd.DataFrame,
    impact_col: str = "impact_intensity_raw",
    visibility_col: str = "response_visibility_raw",
) -> tuple[pd.DataFrame, MismatchSummary]:
    """Compute the two complementary diagnostics defined in the thesis.

    Share-based distributional mismatch
    ------------------------------------
    I_tilde_i = I_i / sum_j(I_j)
    R_tilde_i = R_i / sum_j(R_j)
    Delta_i   = R_tilde_i - I_tilde_i
    SMI_i     = 0.5 * |Delta_i|
    SMI       = sum_i(SMI_i)

    The share calculation uses non-negative, pre-standardisation impact and
    visibility intensities. It does not use z-scores, because z-scores can be
    negative and do not define spatial shares.

    Directional standardised residual
    ---------------------------------
    I_z_i = z(log(1 + I_i))
    R_z_i = z(log(1 + R_i))
    SR_i  = I_z_i - R_z_i

    Positive SR indicates under-visibility relative to measured impact; negative
    SR indicates over-visibility relative to measured impact. The sign itself is
    the thesis-defined directional rule. No empirical +/-0.25 cut-off is used.

    The non-negative magnitude surface is min-max rescaled from |SR| to [0, 1],
    matching the thesis description of a normalised grid-based magnitude layer.
    """

    out = df.copy()
    impact = pd.to_numeric(out[impact_col], errors="raise").clip(lower=0.0)
    visibility = pd.to_numeric(out[visibility_col], errors="raise").clip(lower=0.0)

    if impact.sum() <= 0 or visibility.sum() <= 0:
        raise ValueError("Impact and visibility totals must both be positive.")

    # Distributional SMI: raw non-negative intensities -> spatial shares.
    out["impact_share"] = impact / impact.sum()
    out["visibility_share"] = visibility / visibility.sum()
    out["delta_share"] = out["visibility_share"] - out["impact_share"]
    out["smi_contribution"] = 0.5 * out["delta_share"].abs()
    smi = float(out["smi_contribution"].sum())

    # Directional SR: log transform -> z-standardisation -> difference.
    impact_log = np.log1p(impact)
    visibility_log = np.log1p(visibility)
    out["impact_log_z"] = _zscore(impact_log)
    out["visibility_log_z"] = _zscore(visibility_log)
    out["standardised_residual"] = (
        out["impact_log_z"] - out["visibility_log_z"]
    )

    out["mismatch_magnitude"] = _minmax(
        out["standardised_residual"].abs()
    )

    # Numerical equality is treated as approximate balance. This is not an
    # empirical threshold and does not alter the sign interpretation.
    sr = out["standardised_residual"]
    out["diagnostic_direction"] = np.select(
        [sr > 0.0, sr < 0.0],
        ["under_visibility", "over_visibility"],
        default="approximate_balance",
    )

    return out, MismatchSummary(smi=smi, n_units=len(out))
