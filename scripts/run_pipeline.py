from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_mismatch.pipeline import run_pipeline

result, summary = run_pipeline(
    ROOT / "data" / "sample_grid_units.csv",
    ROOT / "outputs" / "synthetic_demo_mismatch_result.csv",
)

print(
    "Synthetic demonstration SMI computed from "
    f"{summary.n_units} sample spatial units: {summary.smi:.3f}"
)
print(
    "This executed value is not presented as the original empirical thesis SMI."
)
print("\nHighest positive SR cells in the synthetic demonstration:")
print(
    result.sort_values("standardised_residual", ascending=False)[
        [
            "grid_id",
            "municipality",
            "standardised_residual",
            "mismatch_magnitude",
            "diagnostic_direction",
        ]
    ]
    .head(5)
    .to_string(index=False)
)
