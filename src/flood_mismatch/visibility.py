from __future__ import annotations
import numpy as np
import pandas as pd

ALLOWED_CATEGORIES = {
    "Evacuation and entrapment",
    "Infrastructure disruption",
    "Health risk",
    "Resource request",
    "Information",
}

def validate_llm_annotations(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "post_id", "timestamp", "language", "category", "response_type",
        "place_mention", "geocoding_cue", "confidence", "rationale"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing annotation fields: {sorted(missing)}")
    unknown = set(df["category"].dropna()) - ALLOWED_CATEGORIES
    if unknown:
        raise ValueError(f"Unknown categories: {sorted(unknown)}")
    if not df["confidence"].between(0, 1).all():
        raise ValueError("confidence must lie in [0, 1].")
    return df.copy()

def add_visibility_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Construct R_i as response/demand visibility, not deployment."""
    out = df.copy()
    out["response_visibility_raw"] = pd.to_numeric(
        out["response_signal_count"], errors="raise"
    )
    out["response_visibility_log"] = np.log1p(out["response_visibility_raw"])
    pop = out["population"].replace(0, np.nan)
    out["visibility_per_10000"] = (
        out["response_visibility_raw"] / pop * 10000
    ).fillna(0.0)
    return out
