#!/usr/bin/env python3
"""Run the sample GeoAI mismatch pipeline and export results."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flood_mismatch.data_loader import load_sample_municipalities
from flood_mismatch.smi import add_mismatch_columns


def main() -> None:
    df = load_sample_municipalities(ROOT / "data" / "sample_municipalities.csv")
    result, smi = add_mismatch_columns(df)
    out = ROOT / "outputs" / "sample_mismatch_result.csv"
    out.parent.mkdir(exist_ok=True)
    result.sort_values("mismatch_residual").to_csv(out, index=False)
    print(f"SMI = {smi.smi:.3f}")
    print(f"Saved: {out}")
    print(result.sort_values("mismatch_residual")[["name", "mismatch_residual", "mismatch_label"]].to_string(index=False))


if __name__ == "__main__":
    main()
