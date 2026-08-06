from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_mismatch.data import load_grid
from flood_mismatch.impact import compute_impact_intensity
from flood_mismatch.mismatch import compute_mismatch
from flood_mismatch.visibility import add_visibility_metrics, validate_llm_annotations


def prepared() -> pd.DataFrame:
    df = load_grid(ROOT / "data" / "sample_grid_units.csv")
    df = compute_impact_intensity(df)
    return add_visibility_metrics(df)


def test_smi_matches_thesis_share_formula_exactly():
    base = prepared()
    result, summary = compute_mismatch(base)

    impact = base["impact_intensity_raw"].astype(float)
    visibility = base["response_visibility_raw"].astype(float)
    expected_impact_share = impact / impact.sum()
    expected_visibility_share = visibility / visibility.sum()
    expected_delta = expected_visibility_share - expected_impact_share
    expected_smi = 0.5 * expected_delta.abs().sum()

    assert np.allclose(result["impact_share"], expected_impact_share)
    assert np.allclose(result["visibility_share"], expected_visibility_share)
    assert np.allclose(result["delta_share"], expected_delta)
    assert np.isclose(summary.smi, expected_smi)
    assert 0.0 <= summary.smi <= 1.0
    assert np.isclose(result["delta_share"].sum(), 0.0)


def test_sr_matches_log_z_difference_exactly():
    base = prepared()
    result, _ = compute_mismatch(base)

    impact_log = np.log1p(base["impact_intensity_raw"].astype(float))
    visibility_log = np.log1p(base["response_visibility_raw"].astype(float))
    impact_z = (impact_log - impact_log.mean()) / impact_log.std(ddof=0)
    visibility_z = (
        visibility_log - visibility_log.mean()
    ) / visibility_log.std(ddof=0)
    expected_sr = impact_z - visibility_z

    assert np.allclose(result["impact_log_z"], impact_z)
    assert np.allclose(result["visibility_log_z"], visibility_z)
    assert np.allclose(result["standardised_residual"], expected_sr)


def test_magnitude_is_minmax_rescaled_absolute_sr():
    result, _ = compute_mismatch(prepared())
    abs_sr = result["standardised_residual"].abs()
    expected = (abs_sr - abs_sr.min()) / (abs_sr.max() - abs_sr.min())

    assert np.allclose(result["mismatch_magnitude"], expected)
    assert np.isclose(result["mismatch_magnitude"].min(), 0.0)
    assert np.isclose(result["mismatch_magnitude"].max(), 1.0)


def test_direction_uses_sr_sign_without_empirical_cutoff():
    result, _ = compute_mismatch(prepared())

    positive = result["standardised_residual"] > 0
    negative = result["standardised_residual"] < 0
    zero = ~(positive | negative)

    assert (result.loc[positive, "diagnostic_direction"] == "under_visibility").all()
    assert (result.loc[negative, "diagnostic_direction"] == "over_visibility").all()
    assert (
        result.loc[zero, "diagnostic_direction"] == "approximate_balance"
    ).all()


def test_visibility_is_not_deployment():
    result, _ = compute_mismatch(prepared())
    assert "response_visibility_raw" in result.columns
    assert "response_teams" not in result.columns


def test_annotation_schema_contains_thesis_core_fields():
    annotations = pd.read_csv(ROOT / "data" / "sample_llm_annotations.csv")
    validated = validate_llm_annotations(annotations)
    required = {
        "location",
        "needs_category",
        "severity_score",
        "sentiment",
        "summary",
    }
    assert required.issubset(validated.columns)


def test_homepage_does_not_present_demo_smi_as_empirical_result():
    app_text = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'm1.metric("Share-based SMI"' not in app_text
    assert 'm1.metric("Demo SMI"' not in app_text
    assert "Synthetic demonstration run" in app_text
    assert "not the empirical thesis result" in app_text
