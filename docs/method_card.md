# Method Card: CV–LLM Flood Mismatch Diagnosis

## Objective

Diagnose spatial mismatch between flood impact and emergency response.

The thesis logic is converted into a minimal demo pipeline:

```text
Satellite / CV impact layer + LLM response layer → Spatial Mismatch Index → planning diagnosis
```

## 1. CV-derived impact side

In the full research setting, the impact layer can be generated from:

- Sentinel-1 SAR backscatter change detection;
- Sentinel-2 NDWI water masks;
- U-Net / segmentation models for flood extent;
- building footprint overlays for damage exposure.

In this demo, impact is represented by a transparent composite score:

```text
impact_score = 0.40 * normalized(flood_area_pct)
             + 0.35 * normalized(damaged_buildings)
             + 0.25 * normalized(displaced_people)
```

## 2. LLM-derived response side

In the full research setting, an LLM extracts from social media, news, reports, and civil-protection bulletins:

- mentioned locality;
- need signal;
- visible response signal;
- implied response gap;
- urgency/sentiment.

In this demo, response is represented by:

```text
response_score = 0.65 * normalized(response_teams)
               + 0.35 * normalized(response_posts)
```

## 3. Spatial Mismatch Index

```text
SMI = 0.5 * Σ | response_share_i - impact_share_i |
```

Interpretation:

- `0.0`: perfect spatial alignment;
- `0.1–0.2`: relatively low mismatch;
- `0.2–0.4`: moderate mismatch;
- `>0.4`: strong mismatch requiring detailed audit.

The demo sample gives an SMI close to the thesis narrative: moderate mismatch, with rural and peripheral units flagged as under-served.

## 4. Planning interpretation

Negative residuals should not be treated as a final accusation. They are screening signals for follow-up review:

- Are roads or bridges cut off?
- Was population density lower but vulnerability higher?
- Did official resources arrive later than social-media signals suggest?
- Were pumps, shelters, sanitation, and medical response deployed in the correct sequence?
- Should decentralized community response nodes be planned in peripheral villages?

## 5. Limitations

- Sample data are synthetic.
- Social media signals can overrepresent vocal and connected populations.
- Response should not always be exactly proportional to impact; life safety, access, timing, and logistics matter.
- Real deployment should include time-series SMI, accessibility/network constraints, and official audit data.
