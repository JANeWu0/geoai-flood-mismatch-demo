from pathlib import Path
import sys
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_mismatch.data import load_grid
from flood_mismatch.impact import compute_impact_intensity
from flood_mismatch.visibility import add_visibility_metrics
from flood_mismatch.mismatch import compute_mismatch

def prepared():
    df = load_grid(ROOT/"data"/"sample_grid_units.csv")
    df = compute_impact_intensity(df)
    return add_visibility_metrics(df)

def test_smi_distributional_properties():
    result, summary = compute_mismatch(prepared())
    assert 0 <= summary.smi <= 1
    assert np.isclose(result["impact_share"].sum(), 1)
    assert np.isclose(result["visibility_share"].sum(), 1)
    assert np.isclose(result["delta_share"].sum(), 0)
    assert np.isclose(result["smi_contribution"].sum(), summary.smi)

def test_sr_sign_convention():
    result, _ = compute_mismatch(prepared())
    # G001 is designed as high physical impact with weak visibility.
    g001 = result.loc[result["grid_id"] == "G001"].iloc[0]
    assert g001["standardised_residual"] > 0
    assert g001["diagnostic_direction"] == "under_visibility"

def test_visibility_is_not_deployment():
    result, _ = compute_mismatch(prepared())
    assert "response_visibility_raw" in result.columns
    assert "response_teams" not in result.columns
