# Validation

## Scope

Validation in this repository covers the executable diagnostic prototype:

- input schema and value ranges;
- the exact share-based SMI formula;
- the exact log-z standardised residual formula;
- min-max rescaling of `|SR|` to `[0, 1]`;
- sign-based directional interpretation without an empirical `±0.25` cut-off;
- the thesis-core LLM annotation fields;
- explicit separation between visibility and operational deployment.
- explicit separation between the original 5 km thesis figures and the
  post-thesis 1 km refinement figures.

It does **not** independently validate the original empirical thesis maps or
reconstruct the complete original CV, GIS, API and geocoding pipeline.

Static map files are checked for paired filenames and non-zero image content,
but repository tests do not independently recompute the empirical map values.

## Pipeline

Run:

```bash
python scripts/run_pipeline.py
```

The script reports a value in the following form:

```text
Synthetic demonstration SMI computed from 12 sample spatial units: <calculated value>
This executed value is not presented as the original empirical thesis SMI.
```

The numerical value depends on the current contents of
`data/sample_grid_units.csv`; it is not a fixed case-study constant.

## Tests

Run:

```bash
pytest -q
```

Expected result for this revision:

```text
9 passed
```

The tests independently reconstruct the SMI and SR formulas from the input
columns instead of only checking broad ranges. They also verify the magnitude
normalisation, sign convention, annotation schema and homepage evidence label.

## Notebook

`notebooks/Thesis_Aligned_Mismatch_Diagnosis.ipynb` is a synthetic walkthrough.
Any output number shown there must be labelled as an executed demonstration
result rather than as the empirical thesis-wide SMI.
