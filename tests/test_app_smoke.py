"""Execute the actual Streamlit app, not just the numerical helpers.

This checks Python-side startup and page construction. It does not test the
Community Cloud deployment, browser rendering, or external basemap tile access.
"""
from pathlib import Path
import shutil

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TABS = [
    "Integrated Framework",
    "Physical Impact I",
    "Response Visibility R",
    "SMI and SR",
    "5 km vs 1 km Maps",
    "Planning Interpretation",
    "Data and Provenance",
]


def test_app_starts_and_builds_all_tabs(tmp_path):
    # The pipeline writes an output CSV. Isolate this run from tracked outputs.
    app_root = tmp_path / "app"
    app_root.mkdir()
    shutil.copy2(ROOT / "app.py", app_root / "app.py")
    for directory in ("src", "data", "assets", "docs", "prompts"):
        shutil.copytree(ROOT / directory, app_root / directory)

    app = AppTest.from_file(str(app_root / "app.py"), default_timeout=120)
    app.run()

    errors = [str(error.message) for error in app.exception]
    assert not errors, "Streamlit startup failed:\n" + "\n".join(errors)
    assert [tab.label for tab in app.tabs] == EXPECTED_TABS
    assert len(app.get("plotly_chart")) == 3
    assert (app_root / "outputs" / "synthetic_demo_mismatch_result.csv").is_file()
