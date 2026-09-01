# Source and Provenance

## Relationship to the master thesis

This repository follows the final thesis:

**Operationalizing Mismatch Diagnosis in Urban Flood Governance:  
A Multimodal Vision–Language Framework for Dynamic Impact–Response Coordination**

The code is organised around the same analytical sequence used in the thesis:

1. construct physical impact on common spatial units;
2. reconstruct response and demand visibility from geocoded text;
3. calculate the share-based Spatial Mismatch Index;
4. map mismatch direction with the standardised residual;
5. interpret the results through accessibility, governance and planning conditions.

## What comes directly from the thesis

The following definitions and data-accounting statements are taken from the submitted thesis:

- the case is the May 2023 Emilia-Romagna flood;
- the submitted master's-thesis maps use a regular 5 km grid;
- a post-thesis 1 km QGIS refinement is reported separately as a
  scale-sensitivity comparison;
- physical impact is represented by inundation ratio, inundated-building ratio and road-disruption ratio;
- response visibility is a digitally mediated signal and is not equivalent to operational deployment;
- 481 records had usable location assignments, representing 450 unique X post IDs;
- 106 records fall within the May 2023 event window;
- 100 unique X post IDs remain after event-window deduplication;
- the distributional residual is Delta = R share minus I share;
- the overall SMI is one half of the sum of the absolute residuals;
- the directional diagnostic is SR = z(I) minus z(R);
- positive SR means under-visibility relative to impact, while negative SR means over-visibility.

## What is not contained in the supplied PDF

The PDF does not contain the complete raw research package. In particular, it does not provide:

- the original X-post archive;
- API credentials or scraping logs;
- the complete Copernicus, OSM, population and intervention layers;
- the exact 5 km thesis and 1 km refinement attribute tables used to draw
  every map;
- the original LLM run log and manually reviewed annotation sample;
- all original Python and GIS project files.

## Demonstration data

`data/sample_grid_units.csv` and `data/sample_llm_annotations.csv` are synthetic examples. Their purpose is to make the thesis logic executable and reviewable without presenting invented values as empirical results.

The files beginning with `thesis_` contain only source-accounting values explicitly stated in the thesis.

## Published cartographic outputs

The repository contains two clearly separated map directories:

- `assets/maps/5km/`: preserved master's-thesis figures;
- `assets/maps/1km/`: post-thesis QGIS refinements used in the doctoral
  writing-sample scale comparison.

The paired files cover data coverage, physical impact, response visibility,
grid-based mismatch magnitude and the signed residual. The static figures are
empirical/cartographic outputs; the executable 12-unit table remains a
synthetic method demonstration and must not be presented as the source of
those figures.

## Validation scope

A successful run confirms that the formulas, sign conventions, data checks and file outputs work as implemented. It does not independently reproduce the empirical maps or validate the original flood-event dataset.
