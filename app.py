from pathlib import Path
import sys
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# Project paths
# ============================================================

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
FRAMEWORK_ASSETS = ASSETS / "frameworks"
MAP_5KM_ASSETS = ASSETS / "maps" / "5km"
MAP_1KM_ASSETS = ASSETS / "maps" / "1km"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flood_mismatch.pipeline import run_pipeline


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="GeoAI Flood Mismatch Diagnosis",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Light academic theme
# ============================================================

st.markdown(
    """
<style>
:root {
    --paper: #fbfaf6;
    --ink: #202938;
    --muted: #667085;
    --border: #d8dee8;
    --impact: #6f9ed6;
    --response: #9a7fc7;
    --fusion: #d2ad5e;
    --mismatch: #df8d78;
    --planning: #79b89d;
}

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--paper) !important;
    color: var(--ink) !important;
}

[data-testid="stHeader"] {
    background: rgba(251, 250, 246, 0.96) !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1500px;
    padding-top: 1.35rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4, p, li, span, div, label {
    color: var(--ink);
}

.hero-kicker {
    color: var(--muted) !important;
    font-size: 0.76rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.hero-title {
    font-size: 2.45rem;
    line-height: 1.08;
    letter-spacing: -0.035em;
    font-weight: 720;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    max-width: 1040px;
    color: var(--muted) !important;
    font-size: 1.03rem;
    line-height: 1.55;
    margin-bottom: 1.2rem;
}

.research-note {
    margin: 0.45rem 0 1.25rem 0;
    padding: 0.85rem 1rem;
    border-left: 5px solid var(--fusion);
    border-radius: 0 12px 12px 0;
    background: rgba(210, 173, 94, 0.10);
    color: #4c596c !important;
}

div[data-testid="stMetric"] {
    min-height: 108px;
    padding: 0.95rem 1rem;
    background: rgba(255, 255, 255, 0.68);
    border: 1px solid var(--border);
    border-radius: 16px;
}

div[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.85rem;
}

div[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-size: 1.95rem;
}

button[data-baseweb="tab"] {
    color: #586579 !important;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #b55365 !important;
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 12px;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.50);
}

.small-note {
    color: var(--muted) !important;
    font-size: 0.87rem;
    line-height: 1.5;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 2rem;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Data
# ============================================================

@st.cache_data(show_spinner=False)
def load_results():
    return run_pipeline(
        ROOT / "data" / "sample_grid_units.csv",
        ROOT / "outputs" / "synthetic_demo_mismatch_result.csv",
    )


result, summary = load_results()


# ============================================================
# Helpers
# ============================================================

def safe_numeric(series: pd.Series, floor: float = 0.0) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(floor)
    return values.clip(lower=floor)


def show_formula_row(items):
    columns = st.columns(len(items))

    for column, item in zip(columns, items):
        with column:
            with st.container(border=True):
                st.caption(item["label"])
                st.latex(item["formula"])
                st.markdown(
                    '<div class="small-note">{}</div>'.format(item["note"]),
                    unsafe_allow_html=True,
                )


def show_map(
    dataframe: pd.DataFrame,
    value_column: str,
    title: str,
    colour_scale: str,
    size_column: Optional[str] = None,
) -> None:
    required = {"latitude", "longitude", value_column}

    if not required.issubset(dataframe.columns):
        st.warning(
            "The map cannot be drawn because `{}` or the coordinate "
            "columns are missing.".format(value_column)
        )
        return

    map_data = dataframe.copy()
    map_data[value_column] = pd.to_numeric(
        map_data[value_column],
        errors="coerce",
    )

    size_argument = None

    if size_column and size_column in map_data.columns:
        map_data["_marker_size"] = (
            safe_numeric(map_data[size_column], floor=0.01) + 0.01
        )
        size_argument = "_marker_size"

    hover_data = {}

    for column in [
        "grid_id",
        "impact_share",
        "visibility_share",
        "standardised_residual",
        "mismatch_magnitude",
        "diagnostic_direction",
    ]:
        if column in map_data.columns:
            hover_data[column] = True

    figure = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        color=value_column,
        size=size_argument,
        hover_name=(
            "municipality"
            if "municipality" in map_data.columns
            else None
        ),
        hover_data=hover_data,
        color_continuous_scale=colour_scale,
        map_style="carto-positron",
        zoom=6.25,
        height=590,
        title=title,
    )

    figure.update_layout(
        margin=dict(l=0, r=0, t=45, b=45),
        paper_bgcolor="#fbfaf6",
        plot_bgcolor="#fbfaf6",
        font=dict(color="#202938"),
        coloraxis_colorbar=dict(title=""),
    )

    st.plotly_chart(
        figure,
        width="stretch",
        config={"displayModeBar": False},
    )
    st.markdown(
        "<div style='height: 65px;'></div>",
        unsafe_allow_html=True,
    )


def show_scale_pair(
    title: str,
    map_filename: str,
    explanation: str,
) -> None:
    """Show the preserved 5 km thesis map beside the 1 km refinement."""

    st.markdown("### {}".format(title))
    left, right = st.columns(2, gap="large")

    with left:
        st.image(
            MAP_5KM_ASSETS / map_filename,
            caption="Original master's-thesis map (5 km)",
            width="stretch",
        )

    with right:
        st.image(
            MAP_1KM_ASSETS / map_filename,
            caption="Post-thesis QGIS refinement (1 km)",
            width="stretch",
        )

    st.caption(explanation)
    st.divider()


def download_result_button() -> None:
    csv_bytes = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download synthetic demonstration results",
        data=csv_bytes,
        file_name="synthetic_demo_mismatch_result.csv",
        mime="text/csv",
    )


# ============================================================
# Integrated workflow
# All text is deliberately short and positioned inside nodes.
# ============================================================

def integrated_workflow_svg() -> str:
    return """
<div style="background:#fbfaf6;padding:0;margin:0;">
<svg
    viewBox="0 0 1500 820"
    width="100%"
    role="img"
    aria-label="Two parallel CV and LLM streams produce I and R, which are aligned on a common grid and compared through SMI and SR."
    xmlns="http://www.w3.org/2000/svg"
>
    <defs>
        <marker id="arrowBlue"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#6f9ed6"/>
        </marker>

        <marker id="arrowPurple"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#9a7fc7"/>
        </marker>

        <marker id="arrowDark"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>

        <style>
            .node {
                fill: none;
                stroke-width: 4;
            }

            .icon {
                fill: none;
                stroke-width: 3.5;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .phase {
                font: 700 13px Arial, sans-serif;
                letter-spacing: 1.5px;
                fill: #667085;
            }

            .title {
                font: 700 19px Arial, sans-serif;
                fill: #202938;
            }

            .label {
                font: 600 14px Arial, sans-serif;
                fill: #334155;
            }

            .small {
                font: 12px Arial, sans-serif;
                fill: #667085;
            }

            .equation {
                font: italic 17px Georgia, serif;
                fill: #202938;
            }
        </style>
    </defs>

    <!-- Phase labels -->
    <text x="185" y="32" class="phase" text-anchor="middle">INPUT DATA</text>
    <text x="553" y="32" class="phase" text-anchor="middle">PROCESSING</text>
    <text x="860" y="32" class="phase" text-anchor="middle">MODEL OUTPUT</text>
    <text x="1135" y="32" class="phase" text-anchor="middle">COMMON GRID</text>
    <text x="1380" y="32" class="phase" text-anchor="middle">DIAGNOSIS</text>

    <!-- Physical inputs -->
    <rect x="40" y="70"
          width="290" height="255"
          rx="20"
          class="node"
          stroke="#6f9ed6"/>

    <text x="185" y="108" class="title" text-anchor="middle">Physical evidence</text>

    <g transform="translate(67,132)"
       class="icon"
       stroke="#6f9ed6">
        <rect x="42" y="30" width="40" height="30" rx="5"/>
        <path d="M42 37 L17 16"/>
        <path d="M82 37 L107 16"/>
        <path d="M42 55 L17 78"/>
        <path d="M82 55 L107 78"/>
        <circle cx="62" cy="45" r="7"/>
    </g>

    <text x="176" y="160" class="label">Sentinel-1 SAR</text>
    <text x="176" y="188" class="label">Sentinel-2 optical</text>

    <g transform="translate(68,222)"
       class="icon"
       stroke="#63b8c7">
        <path d="M8 52 L8 22 L29 10 L50 22 L50 52 Z"/>
        <path d="M21 52 L21 35 L37 35 L37 52"/>
        <path d="M78 8 C68 24 90 37 78 53"/>
        <path d="M93 8 C83 24 105 37 93 53"/>
    </g>

    <text x="176" y="245" class="label">Copernicus footprint</text>
    <text x="176" y="273" class="label">OSM buildings + roads</text>
    <text x="185" y="298" class="small" text-anchor="middle">Flood and exposure</text>
    <text x="185" y="316" class="small" text-anchor="middle">inputs</text>

    <!-- Arrow to impact processing -->
    <path d="M330 198 L382 198"
          stroke="#6f9ed6"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowBlue)"/>

    <!-- Impact processing -->
    <rect x="390" y="70"
          width="325" height="255"
          rx="20"
          class="node"
          stroke="#6f9ed6"/>

    <text x="553" y="108" class="title" text-anchor="middle">Impact construction</text>
    <text x="425" y="149" class="label">Flood-area overlay</text>
    <text x="425" y="181" class="label">Building exposure</text>
    <text x="425" y="213" class="label">Road disruption</text>
    <text x="425" y="245" class="label">Weighting + QA checks</text>

    <line x1="425" y1="270"
          x2="680" y2="270"
          stroke="#c8d7e8"
          stroke-width="2"/>

    <text x="553" y="302" class="equation" text-anchor="middle">
        Iᵢ = w₁Fᵢ + w₂Bᵢ + w₃Dᵢ
    </text>

    <!-- Impact output -->
    <path d="M715 198 L755 198"
          stroke="#6f9ed6"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowBlue)"/>

    <rect x="765" y="105"
          width="190" height="185"
          rx="20"
          class="node"
          stroke="#6f9ed6"/>

    <text x="860" y="145" class="title" text-anchor="middle">Impact surface</text>
    <text x="860" y="190" class="equation" text-anchor="middle">Iᵢ</text>
    <text x="860" y="224" class="small" text-anchor="middle">5 km / 1 km support</text>
    <text x="860" y="244" class="small" text-anchor="middle">impact intensity</text>
    <text x="860" y="264" class="small" text-anchor="middle">hazard + exposure</text>

    <!-- Textual inputs -->
    <rect x="40" y="445"
          width="290" height="255"
          rx="20"
          class="node"
          stroke="#9a7fc7"/>

    <text x="185" y="483" class="title" text-anchor="middle">Textual evidence</text>

    <g transform="translate(72,510)"
       class="icon"
       stroke="#9a7fc7">
        <path d="M18 5 H82 L101 24 V100 H18 Z"/>
        <path d="M82 5 V24 H101"/>
        <path d="M35 42 H80"/>
        <path d="M35 59 H83"/>
        <path d="M35 76 H69"/>
    </g>

    <text x="196" y="535" class="label">X / social posts</text>
    <text x="196" y="565" class="label">Official bulletins</text>
    <text x="196" y="595" class="label">Contextual reports</text>

    <text x="185" y="649" class="small" text-anchor="middle">481 spatial assignments</text>
    <text x="185" y="677" class="small" text-anchor="middle">106 event-window records</text>

    <!-- Arrow to visibility processing -->
    <path d="M330 573 L382 573"
          stroke="#9a7fc7"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowPurple)"/>

    <!-- Visibility processing -->
    <rect x="390" y="445"
          width="325" height="255"
          rx="20"
          class="node"
          stroke="#9a7fc7"/>

    <text x="553" y="483" class="title" text-anchor="middle">Visibility construction</text>
    <text x="425" y="524" class="label">Fixed LLM prompt + JSON</text>
    <text x="425" y="556" class="label">Need-category coding</text>
    <text x="425" y="588" class="label">NER + place validation</text>
    <text x="425" y="620" class="label">Grid aggregation</text>

    <line x1="425" y1="645"
          x2="680" y2="645"
          stroke="#d9cfea"
          stroke-width="2"/>

    <text x="553" y="677" class="equation" text-anchor="middle">
        Rᵢ = cᵢ
    </text>

    <!-- Visibility output -->
    <path d="M715 573 L755 573"
          stroke="#9a7fc7"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowPurple)"/>

    <rect x="765" y="480"
          width="190" height="185"
          rx="20"
          class="node"
          stroke="#9a7fc7"/>

    <text x="860" y="520" class="title" text-anchor="middle">Visibility surface</text>
    <text x="860" y="565" class="equation" text-anchor="middle">Rᵢ</text>
    <text x="860" y="600" class="small" text-anchor="middle">Raw non-negative</text>
    <text x="860" y="622" class="small" text-anchor="middle">visibility intensity</text>
    <text x="860" y="644" class="small" text-anchor="middle">not deployment</text>

    <!-- Outputs converge on common grid -->
    <path d="M955 198
             C995 198 990 316 1020 342"
          stroke="#6f9ed6"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowDark)"/>

    <path d="M955 573
             C995 573 990 455 1020 425"
          stroke="#9a7fc7"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowDark)"/>

    <!-- Common grid -->
    <rect x="1025" y="255"
          width="220" height="270"
          rx="20"
          class="node"
          stroke="#d2ad5e"/>

    <text x="1135" y="292" class="title" text-anchor="middle">Common spatial</text>
    <text x="1135" y="315" class="title" text-anchor="middle">units</text>

    <g transform="translate(1076,335)"
       class="icon"
       stroke="#d2ad5e">
        <rect x="0" y="0" width="118" height="90" rx="7"/>
        <path d="M39 0 V90"/>
        <path d="M78 0 V90"/>
        <path d="M0 30 H118"/>
        <path d="M0 60 H118"/>
        <circle cx="19" cy="15" r="4"/>
        <circle cx="58" cy="45" r="4"/>
        <circle cx="98" cy="75" r="4"/>
    </g>

    <text x="1135" y="470" class="equation" text-anchor="middle">
        Ĩᵢ = Iᵢ / ΣIⱼ
    </text>

    <text x="1135" y="500" class="equation" text-anchor="middle">
        R̃ᵢ = Rᵢ / ΣRⱼ
    </text>

    <!-- Grid to diagnosis -->
    <path d="M1245 390 L1262 390"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowDark)"/>

    <!-- Mismatch engine -->
    <rect x="1270" y="170"
          width="220" height="450"
          rx="20"
          class="node"
          stroke="#df8d78"/>

    <text x="1380" y="212" class="title" text-anchor="middle">Mismatch</text>

    <text x="1380" y="270" class="equation" text-anchor="middle">
        Δᵢ = R̃ᵢ − Ĩᵢ
    </text>

    <text x="1380" y="330" class="equation" text-anchor="middle">
        SMI = ½Σ|Δᵢ|
    </text>

    <text x="1380" y="390" class="equation" text-anchor="middle">
        SRᵢ = Iᵢᶻ − Rᵢᶻ
    </text>

    <text x="1380" y="450" class="equation" text-anchor="middle">
        Mᵢ = min–max(|SRᵢ|)
    </text>

    <line x1="1300" y1="488"
          x2="1460" y2="488"
          stroke="#edc4b9"
          stroke-width="2"/>

    <text x="1380" y="522" class="label" text-anchor="middle">SRᵢ &gt; 0</text>
    <text x="1380" y="546" class="small" text-anchor="middle">Under-visibility</text>
    <text x="1380" y="576" class="label" text-anchor="middle">SRᵢ &lt; 0</text>
    <text x="1380" y="600" class="small" text-anchor="middle">Over-visibility</text>

    <!-- Planning output -->
    <path d="M1380 620 L1380 650"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#arrowDark)"/>

    <rect x="1025" y="660"
          width="465" height="135"
          rx="20"
          class="node"
          stroke="#79b89d"/>

    <text x="1258" y="700" class="title" text-anchor="middle">Planning interpretation</text>
    <text x="1258" y="735" class="label" text-anchor="middle">
        Access · infrastructure · governance
    </text>
    <text x="1258" y="760" class="label" text-anchor="middle">
        Community capacity · intervention zones
    </text>
    <text x="1258" y="785" class="small" text-anchor="middle">
        Translate diagnostic cells into corridors and service areas
    </text>
</svg>
</div>
    """


# ============================================================
# Horizontal sub-workflows
# ============================================================

def impact_workflow_svg() -> str:
    return """
<svg viewBox="0 0 1400 330"
     width="100%"
     role="img"
     aria-label="Physical impact workflow"
     xmlns="http://www.w3.org/2000/svg">

    <defs>
        <marker id="impactArrow"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>

        <style>
            .n { fill:none; stroke:#6f9ed6; stroke-width:4; }
            .t { font:700 19px Arial,sans-serif; fill:#202938; }
            .l { font:14.5px Arial,sans-serif; fill:#475569; }
            .e { font:italic 17px Georgia,serif; fill:#202938; }
        </style>
    </defs>

    <rect x="20" y="65" width="285" height="205" rx="18" class="n"/>
    <text x="52" y="105" class="t">Source layers</text>
    <text x="52" y="145" class="l">Copernicus EMS flood extent</text>
    <text x="52" y="180" class="l">OSM building footprints</text>
    <text x="52" y="215" class="l">Inundated road segments</text>
    <text x="52" y="250" class="l">5 km thesis / 1 km check</text>

    <path d="M305 168 L372 168"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#impactArrow)"/>

    <rect x="382" y="65" width="400" height="205" rx="18" class="n"/>
    <text x="416" y="105" class="t">Spatial measurement</text>
    <text x="416" y="145" class="l">Fᵢ  inundation ratio</text>
    <text x="416" y="180" class="l">Bᵢ  inundated-building ratio</text>
    <text x="416" y="215" class="l">Dᵢ  road-disruption ratio</text>
    <text x="416" y="250" class="e">Iᵢ = w₁Fᵢ + w₂Bᵢ + w₃Dᵢ</text>

    <path d="M782 168 L850 168"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#impactArrow)"/>

    <rect x="860" y="65" width="260" height="205" rx="18" class="n"/>
    <text x="894" y="105" class="t">Comparable surface</text>
    <text x="894" y="152" class="e">Iᵢ</text>
    <text x="894" y="191" class="l">Log transformation</text>
    <text x="894" y="226" class="l">Z-standardisation</text>

    <path d="M1120 168 L1188 168"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#impactArrow)"/>

    <rect x="1198" y="65" width="180" height="205" rx="18" class="n"/>
    <text x="1231" y="105" class="t">Outputs</text>
    <text x="1231" y="150" class="l">Impact map</text>
    <text x="1231" y="185" class="l">Grid ranking</text>
    <text x="1231" y="220" class="l">QA checks</text>
</svg>
    """


def response_workflow_svg() -> str:
    return """
<svg viewBox="0 0 1400 350"
     width="100%"
     role="img"
     aria-label="Response visibility workflow"
     xmlns="http://www.w3.org/2000/svg">

    <defs>
        <marker id="responseArrow"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>

        <style>
            .n { fill:none; stroke:#9a7fc7; stroke-width:4; }
            .t { font:700 19px Arial,sans-serif; fill:#202938; }
            .l { font:14.5px Arial,sans-serif; fill:#475569; }
            .e { font:italic 17px Georgia,serif; fill:#202938; }
            .s { font:13px Arial,sans-serif; fill:#667085; }
        </style>
    </defs>

    <rect x="20" y="70" width="260" height="215" rx="18" class="n"/>
    <text x="52" y="110" class="t">Text corpus</text>
    <text x="52" y="151" class="l">481 usable locations</text>
    <text x="52" y="186" class="l">450 unique X post IDs</text>
    <text x="52" y="221" class="l">106 event-window records</text>
    <text x="52" y="256" class="l">100 deduplicated posts</text>

    <path d="M280 178 L345 178"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#responseArrow)"/>

    <rect x="355" y="70" width="340" height="215" rx="18" class="n"/>
    <text x="390" y="110" class="t">LLM extraction</text>
    <text x="390" y="151" class="l">Fixed prompt + JSON schema</text>
    <text x="390" y="186" class="l">Location + needs category</text>
    <text x="390" y="221" class="l">Severity + sentiment + summary</text>
    <text x="390" y="256" class="s">Manual subsample check</text>

    <path d="M695 178 L760 178"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#responseArrow)"/>

    <rect x="770" y="70" width="310" height="215" rx="18" class="n"/>
    <text x="805" y="110" class="t">Spatialisation</text>
    <text x="805" y="151" class="l">NER + place-name validation</text>
    <text x="805" y="186" class="l">Geocoding + grid assignment</text>
    <text x="805" y="221" class="l">Semantic count cᵢ</text>
    <text x="805" y="256" class="e">Rᵢ = cᵢ</text>

    <path d="M1080 178 L1145 178"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#responseArrow)"/>

    <rect x="1155" y="70" width="220" height="215" rx="18" class="n"/>
    <text x="1188" y="110" class="t">Outputs</text>
    <text x="1188" y="151" class="l">Visibility R</text>
    <text x="1188" y="186" class="l">Per-capita rate</text>
    <text x="1188" y="221" class="l">Coverage / bias lens</text>
    <text x="1188" y="256" class="s">Not deployment volume</text>
</svg>
    """


def mismatch_workflow_svg() -> str:
    return """
<svg viewBox="0 0 1450 430"
     width="100%"
     role="img"
     aria-label="Mismatch workflow combining impact and visibility shares"
     xmlns="http://www.w3.org/2000/svg">

    <defs>
        <marker id="mismatchArrow"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>

        <style>
            .n { fill:none; stroke-width:4; }
            .t { font:700 20px Arial,sans-serif; fill:#202938; }
            .l { font:14.5px Arial,sans-serif; fill:#475569; }
            .e { font:italic 18px Georgia,serif; fill:#202938; }
        </style>
    </defs>

    <rect x="25" y="52" width="270" height="135" rx="18"
          class="n" stroke="#6f9ed6"/>
    <text x="58" y="92" class="t">Impact share</text>
    <text x="58" y="138" class="e">Ĩᵢ = Iᵢ / ΣIⱼ</text>

    <rect x="25" y="243" width="270" height="135" rx="18"
          class="n" stroke="#9a7fc7"/>
    <text x="58" y="283" class="t">Visibility share</text>
    <text x="58" y="329" class="e">R̃ᵢ = Rᵢ / ΣRⱼ</text>

    <path d="M295 120 C375 120 392 184 468 184"
          stroke="#6f9ed6"
          stroke-width="4"
          fill="none"
          marker-end="url(#mismatchArrow)"/>

    <path d="M295 311 C375 311 392 246 468 246"
          stroke="#9a7fc7"
          stroke-width="4"
          fill="none"
          marker-end="url(#mismatchArrow)"/>

    <rect x="478" y="126" width="305" height="180" rx="18"
          class="n" stroke="#d2ad5e"/>
    <text x="515" y="168" class="t">Share residual</text>
    <text x="515" y="218" class="e">Δᵢ = R̃ᵢ − Ĩᵢ</text>
    <text x="515" y="260" class="l">Unit-level distributional difference</text>

    <path d="M783 216 L855 216"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#mismatchArrow)"/>

    <rect x="865" y="55" width="250" height="135" rx="18"
          class="n" stroke="#df8d78"/>
    <text x="900" y="96" class="t">Global index</text>
    <text x="900" y="143" class="e">SMI = ½Σ|Δᵢ|</text>

    <rect x="865" y="240" width="250" height="135" rx="18"
          class="n" stroke="#c97d92"/>
    <text x="900" y="281" class="t">Directional surface</text>
    <text x="900" y="328" class="e">SRᵢ = Iᵢᶻ − Rᵢᶻ</text>

    <path d="M1115 122 C1172 122 1180 170 1237 170"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#mismatchArrow)"/>

    <path d="M1115 307 C1172 307 1180 252 1237 252"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#mismatchArrow)"/>

    <rect x="1247" y="118" width="180" height="195" rx="18"
          class="n" stroke="#79b89d"/>
    <text x="1277" y="159" class="t">Interpretation</text>
    <text x="1277" y="205" class="l">SRᵢ &gt; 0</text>
    <text x="1277" y="231" class="l">Under-visibility</text>
    <text x="1277" y="271" class="l">SRᵢ &lt; 0</text>
    <text x="1277" y="297" class="l">Over-visibility</text>
</svg>
    """


def planning_workflow_svg() -> str:
    return """
<svg viewBox="0 0 1400 400"
     width="100%"
     role="img"
     aria-label="Planning workflow translating mismatch mechanisms into interventions"
     xmlns="http://www.w3.org/2000/svg">

    <defs>
        <marker id="planningArrow"
                markerWidth="10"
                markerHeight="10"
                refX="8"
                refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>

        <style>
            .n { fill:none; stroke-width:4; }
            .t { font:700 19px Arial,sans-serif; fill:#202938; }
            .l { font:14px Arial,sans-serif; fill:#475569; }
        </style>
    </defs>

    <rect x="25" y="105" width="255" height="190" rx="18"
          class="n" stroke="#df8d78"/>
    <text x="58" y="145" class="t">Diagnosed mechanisms</text>
    <text x="58" y="187" class="l">Accessibility loss</text>
    <text x="58" y="220" class="l">Information gaps</text>
    <text x="58" y="253" class="l">Urban visibility bias</text>

    <path d="M280 200 L350 200"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#planningArrow)"/>

    <rect x="360" y="35" width="280" height="145" rx="18"
          class="n" stroke="#6f9ed6"/>
    <text x="394" y="76" class="t">Spatial planning</text>
    <text x="394" y="117" class="l">Resilient access corridors</text>
    <text x="394" y="148" class="l">Distributed refuge hubs</text>

    <rect x="360" y="220" width="280" height="145" rx="18"
          class="n" stroke="#79b89d"/>
    <text x="394" y="261" class="t">Watershed / NbS</text>
    <text x="394" y="302" class="l">Retention landscapes</text>
    <text x="394" y="333" class="l">Sponge-city retrofits</text>

    <path d="M640 108 C710 108 716 164 785 164"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#planningArrow)"/>

    <path d="M640 292 C710 292 716 235 785 235"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#planningArrow)"/>

    <rect x="795" y="35" width="280" height="145" rx="18"
          class="n" stroke="#9a7fc7"/>
    <text x="829" y="76" class="t">Institutional reform</text>
    <text x="829" y="117" class="l">Integrated data hub</text>
    <text x="829" y="148" class="l">Transparent escalation rules</text>

    <rect x="795" y="220" width="280" height="145" rx="18"
          class="n" stroke="#d2ad5e"/>
    <text x="829" y="261" class="t">Community capacity</text>
    <text x="829" y="302" class="l">Local response teams</text>
    <text x="829" y="333" class="l">Redundant reporting channels</text>

    <path d="M1075 108 C1145 108 1152 165 1212 165"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#planningArrow)"/>

    <path d="M1075 292 C1145 292 1152 235 1212 235"
          stroke="#475569"
          stroke-width="4"
          fill="none"
          marker-end="url(#planningArrow)"/>

    <rect x="1222" y="115" width="155" height="180" rx="18"
          class="n" stroke="#c97d92"/>
    <text x="1250" y="155" class="t">Outcome</text>
    <text x="1250" y="199" class="l">Lower mismatch</text>
    <text x="1250" y="232" class="l">Better alignment</text>
    <text x="1250" y="265" class="l">Greater equity</text>
</svg>
    """


# ============================================================
# Header
# ============================================================

st.markdown(
    """
<div class="hero-kicker">Master thesis companion prototype</div>
<div class="hero-title">Flood Impact–Visibility Mismatch Diagnosis</div>
<div class="hero-subtitle">
    A thesis-aligned diagnostic prototype comparing physical impact
    <b>I</b> with digitally mediated response and demand visibility <b>R</b>
    through a share-based <b>SMI</b> and a directional standardised residual
    <b>SR</b>.
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="research-note">
    <b>Empirical study represented by this interface.</b>
    The thesis analyses the May 2023 Emilia–Romagna flood by aligning
    physical impact <b>I</b> and digitally mediated response/demand
    visibility <b>R</b> on a regular <b>5 km grid</b>. This repository now
    preserves those original thesis maps and places a post-thesis
    <b>1 km QGIS refinement</b> beside them. The finer maps apply the same
    diagnostic definitions as a scale-sensitivity comparison; they do not
    retrospectively replace the thesis analysis.
</div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Case study",
    "Emilia–Romagna",
)

m2.metric("Original thesis unit", "5 km grid")

m3.metric("Post-thesis refinement", "1 km grid")

m4.metric(
    "Analytical posts",
    "100",
)

st.caption(
    "Dataset accounting: 481 usable location assignments; 450 unique X "
    "post IDs; 106 event-window records; "
    "100 deduplicated analytical observations. Ravenna (81) and Faenza (23) "
    "dominate the event-window records, while Conselice and Sant’Agata sul "
    "Santerno appear once each."
)

st.caption(
    "Interactive-demo boundary: the calculations, maps and downloadable "
    "results below use 12 synthetic demonstration units. Any SMI calculated "
    "by this app is a result of that input table and is not the original "
    "empirical thesis SMI."
)

# ============================================================
# Tabs
# ============================================================

tabs = st.tabs(
    [
        "Integrated Framework",
        "Physical Impact I",
        "Response Visibility R",
        "SMI and SR",
        "5 km vs 1 km Maps",
        "Planning Interpretation",
        "Data and Provenance",
    ]
)


# ============================================================
# Integrated framework
# ============================================================

with tabs[0]:
    st.subheader("Integrated CV–LLM methodology")

    st.caption(
        "Two analytically separate streams produce I and R. "
        "They are aligned on consistent spatial units before "
        "distributional and directional mismatch diagnosis."
    )

    components.html(
        integrated_workflow_svg(),
        height=850,
        scrolling=False,
    )

    show_formula_row(
        [
            {
                "label": "Raw physical impact I",
                "formula": r"I_i = w_1F_i + w_2B_i + w_3D_i",
                "note": (
                    "F = inundation ratio; B = inundated-building ratio; "
                    "D = road-disruption ratio. Equal weights are the "
                    "transparent public baseline, not calibrated constants."
                ),
            },
            {
                "label": "Raw response/demand visibility R",
                "formula": r"R_i = c_i",
                "note": (
                    "c is the non-negative count/intensity of semantically "
                    "filtered and geocoded signals in spatial unit i."
                ),
            },
            {
                "label": "Share-based spatial mismatch",
                "formula": (
                    r"SMI=\frac{1}{2}\sum_i"
                    r"\left|\widetilde{R}_i-\widetilde{I}_i\right|"
                ),
                "note": (
                    "The shares are formed from raw non-negative I and R. "
                    "The log-z transformation is used separately for SR."
                ),
            },
        ]
    )

    st.markdown("### Original thesis framework figures")
    st.caption(
        "These two source figures are the same framework panels retained "
        "in the doctoral writing sample. They are displayed without "
        "redrawing or recolouring."
    )

    framework_left, framework_right = st.columns(2, gap="large")

    with framework_left:
        st.image(
            FRAMEWORK_ASSETS / "research_structure.png",
            caption="Overall research structure and analytical workflow",
            width="stretch",
        )

    with framework_right:
        st.image(
            FRAMEWORK_ASSETS / "methodology_framework.png",
            caption="CV–LLM mismatch-diagnosis methodology",
            width="stretch",
        )


# ============================================================
# Physical impact I
# ============================================================

with tabs[1]:
    st.subheader("Physical impact reconstruction")

    components.html(
        impact_workflow_svg(),
        height=340,
        scrolling=False,
    )

    st.markdown(
        """
        The impact layer combines the authoritative Copernicus EMS event
        footprint with OSM building and transport features. Three ratios
        are computed on a common grid: the thesis maps use 5 km cells and
        the post-thesis refinement uses 1 km cells. The indicators are
        inundation, inundated buildings, and road disruption. Their weighted
        combination forms the physical impact intensity **I**.
        """
    )

    if "impact_intensity_raw" in result.columns:
        show_map(
            result,
            value_column="impact_intensity_raw",
            size_column="impact_intensity_raw",
            title="Synthetic demonstration: physical impact intensity I",
            colour_scale="Blues",
        )

    impact_columns = [
        column
        for column in [
            "grid_id",
            "municipality",
            "inundation_ratio",
            "inundated_building_ratio",
            "road_disruption_ratio",
            "impact_intensity_raw",
            "impact_share",
        ]
        if column in result.columns
    ]

    if impact_columns:
        with st.expander(
            "View underlying physical-impact grid data",
            expanded=False,
        ):
            sort_column = (
                "impact_intensity_raw"
                if "impact_intensity_raw" in impact_columns
                else impact_columns[-1]
            )

            st.dataframe(
                result[impact_columns].sort_values(
                    sort_column,
                    ascending=False,
                ),
                width="stretch",
                hide_index=True,
            )


# ============================================================
# Response visibility R
# ============================================================

with tabs[2]:
    st.subheader("Response and demand visibility reconstruction")

    components.html(
        response_workflow_svg(),
        height=360,
        scrolling=False,
    )

    st.markdown(
        """
        The response branch uses a fixed LLM prompt and structured JSON
        output to classify location, need category, severity, sentiment,
        and summary. NER and place-name validation support geocoding.
        Semantically filtered posts are aggregated to the same grid as I.
        The resulting **R** surface represents visibility, not deployment.
        """
    )

    show_formula_row(
        [
            {
                "label": "Raw visibility intensity",
                "formula": r"R_i=c_i",
                "note": (
                    "This non-negative raw intensity forms the visibility "
                    "share used by the SMI."
                ),
            },
            {
                "label": "Standardised visibility for SR",
                "formula": r"R_i^{(z)}=z\!\left[\log(1+R_i)\right]",
                "note": (
                    "Log transformation and z-standardisation are used only "
                    "for the directional residual, not for spatial shares."
                ),
            },
            {
                "label": "Evidence boundary",
                "formula": r"R_i \neq operational\ deployment_i",
                "note": (
                    "Low visibility can reflect reporting and connectivity "
                    "constraints and requires independent triangulation."
                ),
            },
        ]
    )

    response_value = (
        "visibility_per_10000"
        if "visibility_per_10000" in result.columns
        else "response_visibility_raw"
    )

    if response_value in result.columns:
        show_map(
            result,
            value_column=response_value,
            size_column=(
                "response_visibility_raw"
                if "response_visibility_raw" in result.columns
                else response_value
            ),
            title="Synthetic demonstration: response/demand visibility R",
            colour_scale="Purples",
        )

    response_columns = [
        column
        for column in [
            "grid_id",
            "municipality",
            "population",
            "response_signal_count",
            "response_visibility_raw",
            "visibility_per_10000",
            "visibility_share",
        ]
        if column in result.columns
    ]

    if response_columns:
        with st.expander(
            "View underlying response-visibility grid data",
            expanded=False,
        ):
            sort_column = (
                response_value
                if response_value in response_columns
                else response_columns[-1]
            )

            st.dataframe(
                result[response_columns].sort_values(
                    sort_column,
                    ascending=False,
                ),
                width="stretch",
                hide_index=True,
            )


# ============================================================
# SMI and SR
# ============================================================

with tabs[3]:
    st.subheader("Spatial mismatch diagnosis")

    components.html(
        mismatch_workflow_svg(),
        height=445,
        scrolling=False,
    )

    show_formula_row(
        [
            {
                "label": "Share residual",
                "formula": (
                    r"\widetilde I_i=\frac{I_i}{\sum_j I_j},\quad "
                    r"\widetilde R_i=\frac{R_i}{\sum_j R_j},\quad "
                    r"\Delta_i=\widetilde R_i-\widetilde I_i"
                ),
                "note": (
                    "Negative Delta means lower visibility share than impact "
                    "share; positive Delta means the reverse."
                ),
            },
            {
                "label": "Overall distributional mismatch",
                "formula": r"SMI=\frac{1}{2}\sum_i|\Delta_i|",
                "note": (
                    "SMI is calculated from the current dataset and lies in "
                    "[0, 1]. It is not a universal or fixed case value."
                ),
            },
            {
                "label": "Directional residual and magnitude",
                "formula": (
                    r"SR_i=z[\log(1+I_i)]-z[\log(1+R_i)]"
                ),
                "note": (
                    "Positive SR indicates under-visibility; negative SR "
                    "indicates over-visibility. Mismatch magnitude is the "
                    "min-max-rescaled |SR| surface."
                ),
            },
        ]
    )

    with st.expander(
        "Synthetic demonstration run (not empirical thesis result)",
        expanded=False,
    ):
        st.write(
            "Executing the currently loaded {}-unit synthetic table produces "
            "SMI = {:.3f}. This number is calculated from the present sample; "
            "it is not fixed and not the empirical thesis result."
            .format(summary.n_units, summary.smi)
        )

    if "standardised_residual" in result.columns:
        show_map(
            result,
            value_column="standardised_residual",
            size_column=(
                "mismatch_magnitude"
                if "mismatch_magnitude" in result.columns
                else None
            ),
            title="Synthetic demonstration: directional standardised residual SR",
            colour_scale="RdBu_r",
        )

    mismatch_columns = [
        column
        for column in [
            "grid_id",
            "municipality",
            "impact_share",
            "visibility_share",
            "delta_share",
            "impact_log_z",
            "visibility_log_z",
            "standardised_residual",
            "mismatch_magnitude",
            "diagnostic_direction",
        ]
        if column in result.columns
    ]

    if mismatch_columns:
        with st.expander(
            "View ranked mismatch diagnostics",
            expanded=False,
        ):
            sort_column = (
                "standardised_residual"
                if "standardised_residual" in mismatch_columns
                else mismatch_columns[-1]
            )

            st.dataframe(
                result[mismatch_columns].sort_values(
                    sort_column,
                    ascending=False,
                ),
                width="stretch",
                hide_index=True,
            )


# ============================================================
# Original 5 km and refined 1 km maps
# ============================================================

with tabs[4]:
    st.subheader("Original 5 km analysis and post-thesis 1 km refinement")

    st.markdown(
        """
        The left-hand panels are the preserved **5 km maps from the
        master's-thesis analysis**. The right-hand panels are the **1 km
        maps exported from the refreshed QGIS workflow** used for the
        doctoral writing-sample scale comparison. Both resolutions follow
        the same conceptual sequence—impact **I**, visibility **R**,
        distributional mismatch and signed residual—but changing the grid
        also changes aggregation, zero counts, standardisation and class
        breaks.
        """
    )

    st.info(
        "Compare spatial structure and residual direction, not overall "
        "darkness or equal-looking colour shades. The 1 km panels retain "
        "denser OpenStreetMap, building, road, river and boundary context "
        "and are a sensitivity/refinement check, not a replacement for "
        "the thesis result."
    )

    show_scale_pair(
        "Data coverage and signal presence",
        "data_coverage.png",
        (
            "The finer support makes source availability more spatially "
            "selective. Empty cells remain evidence of missing or unobserved "
            "signals, not verified absence of impact or need."
        ),
    )

    show_scale_pair(
        "Physical impact intensity I",
        "impact_intensity.png",
        (
            "The broad affected field remains visible at both scales. The "
            "1 km map resolves narrower corridors and within-cell variation "
            "that the 5 km aggregation smooths."
        ),
    )

    show_scale_pair(
        "Response and demand visibility R",
        "response_visibility.png",
        (
            "The finer grid localises observed communication nodes but also "
            "creates more zero-count cells. Neither map represents deployed "
            "personnel or resources."
        ),
    )

    show_scale_pair(
        "Grid-based mismatch magnitude",
        "smi_magnitude.png",
        (
            "This non-negative cartographic layer identifies where mismatch "
            "is concentrated. It must be distinguished from the single "
            "global SMI value and from the signed residual below."
        ),
    )

    show_scale_pair(
        "Signed standardised residual SR",
        "signed_mismatch.png",
        (
            "Blue indicates impact high relative to visibility; pink "
            "indicates visibility high relative to impact. Exact cell "
            "agreement is not expected after the change in spatial support."
        ),
    )


# ============================================================
# Planning
# ============================================================

with tabs[5]:
    st.subheader("From diagnosis to planning intervention")

    components.html(
        planning_workflow_svg(),
        height=415,
        scrolling=False,
    )

    st.markdown(
        """
        The planning interpretation follows four connected groups:
        spatial planning and infrastructure; watershed management and
        nature-based solutions; emergency-management and institutional
        reform; and community engagement with technology integration.
        The grid is a diagnostic unit. Implementation should translate
        hotspot clusters into access corridors, service areas, drainage
        sub-catchments, or municipal coordination zones.
        """
    )

    st.info(
        "The thesis does not define a validated numerical rule that assigns "
        "a planning action to each grid cell. The four proposal families "
        "shown above are qualitative interpretation pathways, not automated "
        "prescriptions."
    )

    planning_columns = [
        column
        for column in [
            "grid_id",
            "municipality",
            "diagnostic_direction",
            "mismatch_magnitude",
            "road_disruption_ratio",
        ]
        if column in result.columns
    ]

    if planning_columns:
        with st.expander(
            "View diagnostic attributes for qualitative planning review",
            expanded=False,
        ):
            st.dataframe(
                result[planning_columns].sort_values(
                    "mismatch_magnitude",
                    ascending=False,
                ),
                width="stretch",
                hide_index=True,
            )


# ============================================================
# Provenance
# ============================================================

with tabs[6]:
    st.subheader("Data sources, evidence boundary, and reproducibility")

    source_table = pd.DataFrame(
        [
            {
                "Component": "Physical impact I",
                "Sources": (
                    "Copernicus EMS; Sentinel context layers; "
                    "OSM buildings and transport"
                ),
                "Role": (
                    "Inundation, built exposure, transport disruption, "
                    "composite impact"
                ),
            },
            {
                "Component": "Response visibility R",
                "Sources": (
                    "Geocoded X posts; official communications "
                    "used for context"
                ),
                "Role": (
                    "LLM coding, geocoding, grid aggregation, "
                    "visibility reconstruction"
                ),
            },
            {
                "Component": "Mismatch",
                "Sources": "Consistent 5 km thesis grid or 1 km refinement grid",
                "Role": "Raw shares for SMI; log-z fields for SR; min-max |SR| magnitude",
            },
            {
                "Component": "Planning",
                "Sources": (
                    "Accessibility, interventions, governance and "
                    "case interpretation"
                ),
                "Role": (
                    "Translate diagnostic patterns into actionable "
                    "spatial structures"
                ),
            },
        ]
    )

    with st.expander(
        "View data-source and analytical-role table",
        expanded=False,
    ):
        st.dataframe(
            source_table,
            width="stretch",
            hide_index=True,
        )

    st.markdown(
        """
        **Evidence boundary**

        This repository executes a thesis-aligned demonstration
        pipeline. The research materials describe the intended
        geospatial, LLM-assisted, mismatch and planning methodology,
        but the executable repository does not contain every original
        raw raster, API archive, trained model weight, or institutional
        deployment log. The outputs should therefore be presented as a
        reproducible portfolio implementation, not as a recovered copy
        of every original empirical processing step.
        """
    )

    st.markdown(
        """
        **Run and validate**

        ```bash
        python scripts/run_pipeline.py
        pytest -q
        streamlit run app.py
        ```
        """
    )

    download_result_button()


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Flood Impact–Visibility Mismatch Diagnosis · "
    "thesis-aligned synthetic diagnostic prototype · Emilia-Romagna research context"
)
