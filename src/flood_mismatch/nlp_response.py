"""Lightweight LLM-style response signal extraction.

The real thesis workflow uses an LLM to extract locations, needs, response presence,
and sentiment from unstructured disaster text. This demo keeps the default path fully
local and reproducible with a transparent keyword classifier. You can replace
`classify_post` with an OpenAI / local LLM call later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

NEED_KEYWORDS = {
    "need", "waiting", "isolated", "trapped", "no clean water", "no electricity",
    "blocked", "urgent", "not going down", "help", "senza", "isolata",
}
RESPONSE_KEYWORDS = {
    "rescue", "delivering", "volunteers", "firefighters", "civil protection",
    "pumps", "arrived", "food", "team", "thank", "protezione civile",
}


@dataclass(frozen=True)
class PostSignal:
    label: str
    confidence: float
    matched_keywords: tuple[str, ...]


def classify_post(text: str) -> PostSignal:
    """Classify a post into need / response / mixed / neutral using simple rules."""
    t = text.lower()
    need_hits = tuple(sorted(k for k in NEED_KEYWORDS if k in t))
    response_hits = tuple(sorted(k for k in RESPONSE_KEYWORDS if k in t))

    if need_hits and response_hits:
        return PostSignal("mixed", 0.65, need_hits + response_hits)
    if need_hits:
        return PostSignal("need", min(0.95, 0.55 + 0.10 * len(need_hits)), need_hits)
    if response_hits:
        return PostSignal("response", min(0.95, 0.55 + 0.10 * len(response_hits)), response_hits)
    return PostSignal("neutral", 0.40, tuple())


def classify_posts(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Add local signal labels to a post dataframe."""
    result = df.copy()
    signals = [classify_post(str(x)) for x in result[text_col]]
    result["predicted_label"] = [s.label for s in signals]
    result["confidence"] = [s.confidence for s in signals]
    result["matched_keywords"] = [", ".join(s.matched_keywords) for s in signals]
    return result


def aggregate_signals(posts: pd.DataFrame, locality_col: str = "locality") -> pd.DataFrame:
    """Aggregate classified posts by locality."""
    if "predicted_label" not in posts.columns:
        posts = classify_posts(posts)
    pivot = (
        posts.pivot_table(index=locality_col, columns="predicted_label", values="post_id", aggfunc="count", fill_value=0)
        .reset_index()
    )
    for col in ["need", "response", "mixed", "neutral"]:
        if col not in pivot.columns:
            pivot[col] = 0
    return pivot[[locality_col, "need", "response", "mixed", "neutral"]]
