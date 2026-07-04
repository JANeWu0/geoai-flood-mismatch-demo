"""Spatial Mismatch Index (SMI) utilities.

SMI = 0.5 * sum_i | R_i / sum(R) - I_i / sum(I) |

Where I is flood impact intensity and R is response intensity. The value is in [0, 1].
0 means perfect spatial alignment; values closer to 1 indicate stronger mismatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SMIResult:
    """Container for SMI output."""

    smi: float
    impact_total: float
    response_total: float
    n_units: int


def _safe_positive_array(values: Iterable[float], name: str) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if len(arr) == 0:
        raise ValueError(f"{name} cannot be empty")
    if np.any(arr < 0):
        raise ValueError(f"{name} cannot contain negative values")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} must contain only finite numbers")
    return arr


def compute_smi(impact: Iterable[float], response: Iterable[float]) -> SMIResult:
    """Compute the Spatial Mismatch Index.

    Parameters
    ----------
    impact:
        Non-negative impact scores by spatial unit.
    response:
        Non-negative response scores by spatial unit, in the same order.

    Returns
    -------
    SMIResult
        SMI value and totals used for normalization.
    """
    impact_arr = _safe_positive_array(impact, "impact")
    response_arr = _safe_positive_array(response, "response")
    if len(impact_arr) != len(response_arr):
        raise ValueError("impact and response must have the same length")

    impact_total = float(impact_arr.sum())
    response_total = float(response_arr.sum())
    if impact_total <= 0:
        raise ValueError("impact total must be greater than zero")
    if response_total <= 0:
        raise ValueError("response total must be greater than zero")

    impact_share = impact_arr / impact_total
    response_share = response_arr / response_total
    smi = float(0.5 * np.abs(response_share - impact_share).sum())
    return SMIResult(smi=smi, impact_total=impact_total, response_total=response_total, n_units=len(impact_arr))


def add_mismatch_columns(
    df: pd.DataFrame,
    impact_col: str = "impact_score",
    response_col: str = "response_score",
) -> tuple[pd.DataFrame, SMIResult]:
    """Return a copy of `df` with SMI shares, residuals, and mismatch labels.

    residual = response_share - impact_share
    negative residual => under-response relative to impact.
    """
    if impact_col not in df.columns:
        raise KeyError(f"Missing impact column: {impact_col}")
    if response_col not in df.columns:
        raise KeyError(f"Missing response column: {response_col}")

    result = df.copy()
    smi_result = compute_smi(result[impact_col], result[response_col])
    result["impact_share"] = result[impact_col] / smi_result.impact_total
    result["response_share"] = result[response_col] / smi_result.response_total
    result["mismatch_residual"] = result["response_share"] - result["impact_share"]

    def label(x: float) -> str:
        if x <= -0.05:
            return "severe_under_response"
        if x < -0.015:
            return "under_response"
        if x > 0.05:
            return "possible_over_response"
        if x > 0.015:
            return "slight_over_response"
        return "aligned"

    result["mismatch_label"] = result["mismatch_residual"].map(label)
    return result, smi_result
