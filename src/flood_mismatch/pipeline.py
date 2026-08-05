from __future__ import annotations
from pathlib import Path
import pandas as pd
from .data import load_grid
from .impact import compute_impact_intensity
from .visibility import add_visibility_metrics
from .mismatch import compute_mismatch
from .planning import add_planning_actions

def run_pipeline(input_csv: str | Path, output_csv: str | Path):
    grid = load_grid(input_csv)
    grid = compute_impact_intensity(grid)
    grid = add_visibility_metrics(grid)
    result, summary = compute_mismatch(grid)
    result = add_planning_actions(result)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)
    return result, summary
