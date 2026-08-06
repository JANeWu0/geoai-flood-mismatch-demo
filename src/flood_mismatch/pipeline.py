from __future__ import annotations

from pathlib import Path

from .data import load_grid
from .impact import compute_impact_intensity
from .mismatch import compute_mismatch
from .visibility import add_visibility_metrics


def run_pipeline(
    input_csv: str | Path,
    output_csv: str | Path,
):
    """Run the executable diagnostic core on the supplied spatial-unit table.

    The repository input is a thesis-aligned synthetic demonstration table. The
    returned SMI is therefore a result of that executed table, not a fixed value
    and not the original empirical thesis-wide SMI.
    """

    grid = load_grid(input_csv)
    grid = compute_impact_intensity(grid)
    grid = add_visibility_metrics(grid)
    result, summary = compute_mismatch(grid)

    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)
    return result, summary
