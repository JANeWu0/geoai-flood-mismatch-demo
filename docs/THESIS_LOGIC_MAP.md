# Thesis-to-Code Logic Map

This repository follows the analytical chain of the final master thesis.

| Thesis section | Repository implementation |
|---|---|
| Ch. 1–2: problem, questions and objectives | `README.md`, notebook introduction |
| Ch. 4: material and source accounting | `data/thesis_source_accounting.csv`, `data/thesis_visibility_counts.csv` |
| 5.1: physical-impact assessment | `src/flood_mismatch/impact.py` |
| 5.1.3: three impact ratios | `inundation_ratio`, `inundated_building_ratio`, `road_disruption_ratio` |
| 5.2: LLM-enabled visibility reconstruction | `src/flood_mismatch/visibility.py`, `prompts/llm_annotation_prompt.md` |
| 5.3: share-based SMI and Delta | `src/flood_mismatch/mismatch.py` |
| 7.3: standardised residual SR and |SR| | `standardised_residual`, `mismatch_magnitude` |
| 7.4: access constraints and recovery context | road-disruption interpretation and optional overlays |
| Ch. 8: strategic proposals | `src/flood_mismatch/planning.py` |
| Ch. 9–12: limitations and outlook | notebook final sections and `SOURCE_AND_PROVENANCE.md` |

## Central interpretation boundary

`R_i` means **response/demand visibility reconstructed from digitally mediated signals**.  
It is not a direct count of deployed teams, vehicles, funding, or completed rescue operations.

## Spatial unit

The thesis case analysis uses a common 1 km grid so that impact and visibility surfaces can be fused directly. The included sample is a small tabular representation of such grid units.
