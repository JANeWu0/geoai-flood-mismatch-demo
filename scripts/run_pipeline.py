from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_mismatch.pipeline import run_pipeline

result, summary = run_pipeline(
    ROOT / "data" / "sample_grid_units.csv",
    ROOT / "outputs" / "thesis_aligned_mismatch_result.csv",
)

print(f"Share-based SMI: {summary.smi:.3f}")
print(f"Spatial units: {summary.n_units}")
print("\nHighest under-visibility cells (positive SR):")
print(
    result.sort_values("standardised_residual", ascending=False)[
        ["grid_id", "municipality", "standardised_residual",
         "mismatch_magnitude", "diagnostic_direction"]
    ].head(5).to_string(index=False)
)
