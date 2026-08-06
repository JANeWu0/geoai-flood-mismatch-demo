from __future__ import annotations

import numpy as np
import pandas as pd


THESIS_NEEDS_CATEGORIES = {
    "Evacuation",
    "Infrastructure failure",
    "Health risk",
    "Resource request",
    "Information",
}

THESIS_SENTIMENTS = {
    "anxiety",
    "anger",
    "desperation",
    "gratitude",
    "neutral",
    "other",
}


def validate_llm_annotations(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the thesis-core annotation fields plus optional audit fields.

    Thesis Chapter 5.2.2 describes the core fields as location, needs category,
    severity score (1-10), sentiment and summary. The repository additionally
    retains post/time/language and optional audit fields so classifications can
    be traced without claiming that those additions were the original thesis
    schema.
    """

    required = {
        "post_id",
        "timestamp",
        "language",
        "location",
        "needs_category",
        "severity_score",
        "sentiment",
        "summary",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing annotation fields: {sorted(missing)}")

    unknown_categories = (
        set(df["needs_category"].dropna()) - THESIS_NEEDS_CATEGORIES
    )
    if unknown_categories:
        raise ValueError(
            f"Unknown needs categories: {sorted(unknown_categories)}"
        )

    severity = pd.to_numeric(df["severity_score"], errors="raise")
    if not severity.between(1, 10).all():
        raise ValueError("severity_score must lie in [1, 10].")

    unknown_sentiments = set(df["sentiment"].dropna()) - THESIS_SENTIMENTS
    if unknown_sentiments:
        raise ValueError(f"Unknown sentiments: {sorted(unknown_sentiments)}")

    if "confidence" in df.columns:
        confidence = pd.to_numeric(df["confidence"], errors="raise")
        if not confidence.between(0, 1).all():
            raise ValueError("confidence must lie in [0, 1].")

    return df.copy()


def add_visibility_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Construct non-negative response/demand visibility R_i.

    R_i is the spatial intensity of digitally mediated response, demand and
    information signals. It is not operational deployment. The raw non-negative
    intensity is used to form SMI shares; log and z transformations are applied
    later, only for the directional standardised residual.
    """

    out = df.copy()
    out["response_visibility_raw"] = pd.to_numeric(
        out["response_signal_count"], errors="raise"
    ).clip(lower=0.0)
    out["response_visibility_log"] = np.log1p(
        out["response_visibility_raw"]
    )

    population = pd.to_numeric(out["population"], errors="raise").replace(
        0, np.nan
    )
    out["visibility_per_10000"] = (
        out["response_visibility_raw"] / population * 10000
    ).fillna(0.0)
    return out
