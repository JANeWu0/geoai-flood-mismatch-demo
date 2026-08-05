# Operationalizing Mismatch Diagnosis in Urban Flood Governance

## Thesis-aligned Python portfolio

This repository operationalises the analytical logic of the master thesis:

**Operationalizing Mismatch Diagnosis in Urban Flood Governance:  
A Multimodal Vision–Language Framework for Dynamic Impact–Response Coordination**

**Author:** Wu Huijuan  
**Programme:** Transforming City Regions, RWTH Aachen University  
**Case:** May 2023 Emilia-Romagna flood

## 1. Research problem

The project asks whether the spatial distribution of realised flood impacts is aligned with the spatial distribution of response- and demand-related visibility.

The key distinction is:

- **Impact `I_i`**: physically reconstructed flood consequences;
- **Visibility `R_i`**: digitally mediated response and demand signals;
- `R_i` is **not** a direct measurement of operational deployment.

## 2. Analytical framework

The workflow follows four stages:

1. reconstruct physical impact on a common 1 km grid;
2. extract, geocode and aggregate response/demand signals;
3. quantify distributional mismatch with the Spatial Mismatch Index;
4. interpret direction and magnitude through the standardised residual surface.

## 3. Material and source structure

### Physical-impact inputs

- Copernicus EMS Rapid Mapping inundation footprint;
- OpenStreetMap building footprints;
- OpenStreetMap road and rail networks;
- supporting Sentinel, orthophoto, LiDAR, DEM and administrative layers.

### Visibility inputs

- geolocated X posts;
- LLM-assisted semantic annotations;
- official civil-protection texts as contextual references, not deployment counts.

The thesis reports:

- 481 records with usable location assignments;
- 450 unique X post IDs;
- 106 event-window records;
- 100 unique analytical posts after deduplication.

## 4. Physical impact intensity

For each grid cell:

```text
I_i =
w1 * inundation_ratio_i
+ w2 * inundated_building_ratio_i
+ w3 * road_disruption_ratio_i
```

The demo uses equal weights as a transparent baseline. The thesis states that outputs must be interpreted conditionally on the weighting choice because formal calibration and sensitivity testing were not available.

## 5. Response and demand visibility

The LLM annotation schema records:

- location;
- need category;
- response type;
- confidence;
- short rationale.

The thesis categories are represented in `prompts/llm_annotation_prompt.md`. Post counts are aggregated to the same grid and can also be expressed per 10,000 residents.

## 6. Mismatch diagnostics

### Distributional SMI

```text
I_share_i = I_i / sum(I)
R_share_i = R_i / sum(R)
Delta_i = R_share_i - I_share_i
SMI_i = 0.5 * abs(Delta_i)
SMI = sum(SMI_i)
```

Negative `Delta_i` means under-visibility relative to impact.

### Directional standardised residual

```text
SR_i = z(log(1 + I_i)) - z(log(1 + R_i))
```

- positive `SR_i`: under-visibility relative to impact;
- negative `SR_i`: over-visibility relative to impact;
- `|SR_i|`, normalised to `[0, 1]`: mismatch magnitude.

SMI and SR answer different questions and must not be treated as the same metric.

## 7. Case-study interpretation

The diagnostic workflow examines:

- urban concentration of digitally visible signals;
- rural and low-lying agricultural cells with high impact and weak visibility;
- accessibility constraints and road-network disruption;
- post-flood intervention layers as qualitative triangulation.

A high mismatch magnitude is a screening signal requiring further investigation. It is not, by itself, proof of response failure.

## 8. Strategic proposal logic

The code maps diagnosed conditions to the four proposal groups in the thesis:

1. spatial planning and infrastructure;
2. watershed management and nature-based solutions;
3. emergency management and institutional reform;
4. community engagement and technology integration.

## 9. Run the project

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
pytest -q
streamlit run app.py
```

Open the notebook:

```text
notebooks/Thesis_Aligned_Mismatch_Diagnosis.ipynb
```

## 10. Evidence boundary

The executable grid and post-level examples are synthetic. They demonstrate the thesis method without claiming to reproduce the original empirical maps. See:

- `docs/SOURCE_AND_PROVENANCE.md`
- `docs/THESIS_LOGIC_MAP.md`
- `docs/REAL_DATA_REPLACEMENT.md`
