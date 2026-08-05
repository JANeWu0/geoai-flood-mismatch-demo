from __future__ import annotations
import pandas as pd

def assign_planning_response(row: pd.Series) -> str:
    sr = float(row["standardised_residual"])
    magnitude = float(row["mismatch_magnitude"])
    road = float(row["road_disruption_ratio"])

    if sr > 0.25 and road >= 0.5:
        return (
            "Protect critical access links, prepare detours and pre-position assets; "
            "add proactive field verification and redundant reporting channels."
        )
    if sr > 0.25:
        return (
            "Use proactive reconnaissance, redundant reporting channels and local "
            "refuge/coordination nodes."
        )
    if sr < -0.25:
        return (
            "Apply attention-calibration rules and cross-check highly visible cells "
            "against physically reconstructed impact."
        )
    if magnitude >= 0.6:
        return "Investigate with institutional records and intervention overlays."
    return "Maintain monitoring; no strong directional mismatch in the demo."

def add_planning_actions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["planning_action"] = out.apply(assign_planning_response, axis=1)
    return out
