from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flood_mismatch.data_loader import load_sample_municipalities
from flood_mismatch.smi import add_mismatch_columns

st.set_page_config(page_title="GeoAI Flood Mismatch Demo", layout="wide")

st.title("GeoAI Flood Response–Impact Mismatch Demo")
st.caption("CV + LLM + Spatial Mismatch Index (SMI) | Synthetic Emilia-Romagna sample data")

with st.sidebar:
    st.header("Demo controls")
    st.write("This app turns the thesis workflow into a small reproducible GitHub demo.")
    residual_threshold = st.slider("Under-response threshold", min_value=-0.12, max_value=0.0, value=-0.05, step=0.01)
    st.markdown("**Pipeline**")
    st.markdown("1. CV-derived flood impact score\n2. LLM-derived/social response score\n3. SMI mismatch diagnosis\n4. Map + planning interpretation")

@st.cache_data
def load_data() -> pd.DataFrame:
    return load_sample_municipalities(ROOT / "data" / "sample_municipalities.csv")

df = load_data()
result, smi_result = add_mismatch_columns(df)
result["under_response_flag"] = result["mismatch_residual"] <= residual_threshold
result["mismatch_abs"] = result["mismatch_residual"].abs()

col1, col2, col3, col4 = st.columns(4)
col1.metric("SMI", f"{smi_result.smi:.3f}")
col2.metric("Spatial units", smi_result.n_units)
col3.metric("Under-response units", int(result["under_response_flag"].sum()))
col4.metric("Most negative residual", f"{result['mismatch_residual'].min():.3f}")

st.subheader("Mismatch map")
st.write("Negative residual = response share is lower than impact share. Larger circles indicate stronger absolute mismatch.")

# RGB colors as data values, not matplotlib styling.
colors = {
    "severe_under_response": [210, 64, 53, 180],
    "under_response": [240, 160, 60, 170],
    "aligned": [80, 160, 90, 150],
    "slight_over_response": [80, 145, 210, 150],
    "possible_over_response": [70, 95, 190, 150],
}
result["color"] = result["mismatch_label"].map(colors)
result["radius"] = (result["mismatch_abs"] * 55000 + 2500).astype(float)

view_state = pdk.ViewState(latitude=44.25, longitude=12.0, zoom=7.2, pitch=35)
layer = pdk.Layer(
    "ScatterplotLayer",
    data=result,
    get_position="[longitude, latitude]",
    get_radius="radius",
    get_fill_color="color",
    pickable=True,
)
st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{name}\nResidual: {mismatch_residual}\nLabel: {mismatch_label}\n{note}"},
    ),
    use_container_width=True,
)

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Impact share vs. response share")
    long = result.melt(
        id_vars=["name"],
        value_vars=["impact_share", "response_share"],
        var_name="metric",
        value_name="share",
    )
    fig = px.bar(long, x="name", y="share", color="metric", barmode="group")
    fig.update_layout(xaxis_title="Locality", yaxis_title="Share of regional total")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Ranked mismatch residuals")
    ranked = result.sort_values("mismatch_residual")[[
        "name", "province", "urban_class", "impact_share", "response_share", "mismatch_residual", "mismatch_label"
    ]]
    st.dataframe(ranked, use_container_width=True, hide_index=True)

st.subheader("Planning interpretation")
worst = result.sort_values("mismatch_residual").head(3)
st.markdown(
    "\n".join(
        f"- **{row.name}**: {row.mismatch_label.replace('_', ' ')}. Planning response: prioritize mobile pumps, local shelters, redundant road access, and community first-responder nodes."
        for row in worst.itertuples(index=False)
    )
)

st.info("The sample data are synthetic but calibrated to the thesis narrative. Replace data/sample_municipalities.csv with real CV and LLM outputs to reuse the demo.")
