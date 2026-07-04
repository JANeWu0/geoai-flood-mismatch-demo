"""Data loading and feature engineering helpers for the demo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_sample_municipalities(path: str | Path = "data/sample_municipalities.csv") -> pd.DataFrame:
    """Load the synthetic municipality-level demo dataset."""
    df = pd.read_csv(path)
    return build_scores(df)


def _normalized(series: pd.Series) -> pd.Series:
    total = float(series.sum())
    if total <= 0:
        raise ValueError(f"Cannot normalize {series.name}: total must be positive")
    return series.astype(float) / total


def build_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Create composite impact and response scores from tabular signals.

    These weights are intentionally transparent so reviewers can challenge or tune them.
    In a full research pipeline, `impact_score` would come from CV-derived flood extent
    and damage layers, while `response_score` would come from official deployments and
    LLM-extracted response signals.
    """
    required = {
        "flood_area_pct",
        "damaged_buildings",
        "displaced_people",
        "response_posts",
        "response_teams",
    }
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns: {sorted(missing)}")

    result = df.copy()
    result["impact_score"] = (
        0.40 * _normalized(result["flood_area_pct"])
        + 0.35 * _normalized(result["damaged_buildings"])
        + 0.25 * _normalized(result["displaced_people"])
    )
    result["response_score"] = (
        0.65 * _normalized(result["response_teams"])
        + 0.35 * _normalized(result["response_posts"])
    )
    return result
