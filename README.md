# GeoAI Flood Response–Impact Mismatch Demo

> A GitHub-ready GeoAI demo derived from the thesis **“Diagnosing Urban Flood Response-Impact Mismatch from an Architectural Perspective: A CV-LLM Coupled Analysis Based on the 2023 Emilia-Romagna Flood in Italy.”**

中文标题：**CV-LLM 多模态框架下的城市洪灾响应失配诊断 Demo**

This repository converts the thesis idea into a lightweight, reproducible geospatial AI demo: use **computer vision-derived flood impact signals**, **LLM/social response signals**, and a **Spatial Mismatch Index (SMI)** to identify where disaster response is lower than observed flood impact.

The sample dataset is synthetic but calibrated to the thesis narrative. Replace it with your real CV/LLM outputs when publishing the full research version.

---

## What the demo shows

| Thesis component | GitHub demo implementation |
|---|---|
| Remote sensing + CV flood impact assessment | `src/flood_mismatch/remote_sensing.py` + sample impact columns |
| LLM extraction from social/report text | `src/flood_mismatch/nlp_response.py` + `data/sample_social_posts.csv` |
| Spatial Mismatch Index | `src/flood_mismatch/smi.py` |
| Case interpretation | Streamlit app map + residual ranking |
| Planning proposal | `docs/method_card.md` |

Core question:

> Are emergency response resources spatially aligned with where flood impact is highest?

---

## Demo preview

The Streamlit app displays:

1. **SMI score** for the full case sample.
2. **Interactive mismatch map** of affected municipalities.
3. **Impact share vs. response share chart**.
4. **Under-response ranking** for planning diagnosis.

Expected sample result:

```text
SMI ≈ 0.289
Most under-served demo localities: Conselice, Solarolo, Cotignola, Modigliana
```

---

## Quick start

```bash
git clone <your-repo-url>
cd geoai-flood-mismatch-demo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run the pipeline without the UI:

```bash
python scripts/run_pipeline.py
```

This writes:

```text
outputs/sample_mismatch_result.csv
```

---

## Data schema

`data/sample_municipalities.csv` is the main demo table.

| Column | Meaning |
|---|---|
| `name`, `province`, `latitude`, `longitude` | Spatial unit metadata |
| `flood_area_pct` | CV-derived or estimated flooded area percentage |
| `damaged_buildings` | CV-derived or reported building damage count |
| `displaced_people` | affected/displaced population proxy |
| `need_posts` | LLM-extracted distress / unmet need signal count |
| `response_posts` | LLM-extracted visible response signal count |
| `response_teams` | official or reported response deployment proxy |

The demo computes:

```text
impact_score   = weighted normalized flood impact indicators
response_score = weighted normalized response indicators
SMI            = 0.5 * sum(|response_share - impact_share|)
residual       = response_share - impact_share
```

Negative residuals indicate **under-response relative to impact**.

---

## Repository structure

```text
geoai-flood-mismatch-demo/
├── app.py                         # Streamlit map dashboard
├── data/
│   ├── sample_municipalities.csv
│   ├── sample_municipalities.geojson
│   └── sample_social_posts.csv
├── docs/
│   ├── data_card.md
│   ├── method_card.md
│   └── thesis_to_demo_mapping.md
├── prompts/
│   └── extract_response_signal.md
├── scripts/
│   └── run_pipeline.py
├── src/flood_mismatch/
│   ├── data_loader.py
│   ├── nlp_response.py
│   ├── remote_sensing.py
│   └── smi.py
├── tests/
│   └── test_smi.py
└── assets/
    └── architecture.svg
```

---

## How to replace the sample data with real research data

### 1. CV flood impact output

Export one row per spatial unit:

```csv
name,latitude,longitude,flood_area_pct,damaged_buildings,displaced_people
Conselice,44.5114,11.8290,80,160,6000
```

For a production workflow, `flood_area_pct` can come from:

- Sentinel-1 SAR change detection
- Sentinel-2 NDWI water mask
- U-Net / segmentation model output
- Copernicus EMS validation layers

### 2. LLM/social response output

Export extracted response signals:

```csv
locality,need_posts,response_posts,response_teams
Conselice,125,15,3
```

The prompt template in `prompts/extract_response_signal.md` gives a repeatable extraction format.

### 3. Recompute SMI

```bash
python scripts/run_pipeline.py
```

---

## Citation / thesis link

When publishing this repo, cite the thesis and make clear that the included CSV is a synthetic demo dataset unless replaced with verified field, official, satellite, or social-media data.

Suggested short citation:

```bibtex
@mastersthesis{flood_mismatch_geoai_demo,
  title  = {Diagnosing Urban Flood Response-Impact Mismatch from an Architectural Perspective: A CV-LLM Coupled Analysis Based on the 2023 Emilia-Romagna Flood in Italy},
  author = {Your Name},
  year   = {2026},
  note   = {GitHub demo repository}
}
```

---

## 中文说明

这个仓库把你的毕业设计从“论文叙事”转换成“可运行 demo”：

- 用遥感/CV 结果表示洪灾物理影响；
- 用 LLM 对社交媒体、报告、新闻等文本抽取“需求/响应”信号；
- 用 SMI 指数量化每个地区“灾情占比”和“救援占比”的差异；
- 在地图上突出响应不足区域，为城市韧性规划、应急资源配置和海绵城市策略提供诊断依据。

适合作为：

- GitHub portfolio 项目；
- 毕业设计技术展示；
- GeoAI / Urban AI / Climate Resilience 方向作品集；
- 后续论文代码仓库初稿。

---

## License

MIT License. Replace the placeholder author name before publishing.
