# Thesis–code alignment audit

This audit records how the corrected repository follows the methodology and
evidence boundaries stated in the submitted thesis.

## 1. Physical impact

Thesis formulation:

```text
I_i = w1*inundation_ratio_i
    + w2*inundated_building_ratio_i
    + w3*road_disruption_ratio_i
```

Repository implementation: `src/flood_mismatch/impact.py`.

The public baseline uses equal weights. This is a transparent assumption, not a
calibrated empirical truth. The code and interface state that results are
conditional on the weighting choice.

## 2. Response and demand visibility

Thesis meaning:

```text
R_i = digitally mediated response/demand visibility
```

It is not operational deployment.

For the public table:

```text
R_i = c_i
```

where `c_i` is a non-negative semantically filtered and geocoded signal count.
This raw quantity is used for spatial shares.

## 3. Share-based SMI

```text
I_tilde_i = I_i / sum_j(I_j)
R_tilde_i = R_i / sum_j(R_j)
Delta_i = R_tilde_i - I_tilde_i
SMI_i = 0.5*abs(Delta_i)
SMI = sum_i(SMI_i)
```

Implementation: `src/flood_mismatch/mismatch.py`.

The code tests this formula by independently reconstructing the shares and
comparing every output column and the final sum.

## 4. Directional standardised residual

```text
I_z_i = z(log(1 + I_i))
R_z_i = z(log(1 + R_i))
SR_i = I_z_i - R_z_i
```

- `SR_i > 0`: under-visibility relative to measured impact;
- `SR_i < 0`: over-visibility relative to measured impact;
- numerical zero: approximate balance.

The corrected code removes the earlier unsupported `±0.25` threshold.

## 5. Mismatch magnitude

The thesis describes a non-negative `abs(SR)` surface rescaled to `[0, 1]`.
The corrected repository uses documented min-max rescaling:

```text
M_i = (abs(SR_i) - min_j(abs(SR_j)))
      / (max_j(abs(SR_j)) - min_j(abs(SR_j)))
```

This ensures a minimum of 0 and maximum of 1 when the surface is non-constant.

## 6. Numerical-result boundary

The 12-unit input is synthetic. The SMI produced by running that table is an
executed demonstration result. It is not displayed on the homepage and is not
presented as the empirical thesis-wide value.

The number remains available only in clearly labelled technical contexts:

- the command-line run;
- the executed notebook;
- a collapsed Streamlit expander.

Each location explicitly states that it is not the empirical thesis result.

## 7. LLM schema

Thesis-core fields:

- location;
- needs category;
- severity score (1–10);
- sentiment;
- summary.

The public prompt includes these fields. Optional confidence, geocoding cue and
rationale fields are labelled repository audit additions rather than a verbatim
copy of the thesis prompt.

## 8. Planning interpretation

The thesis provides four qualitative proposal groups. It does not define a
validated numerical mapping from grid values to automatic prescriptions. The
corrected pipeline therefore removes threshold-generated planning actions and
presents the proposal groups as qualitative interpretation pathways.

## 9. Public implementation boundary

The thesis develops a CV–LLM multimodal framework. The public repository begins
from prepared unit-level physical-impact ratios and synthetic visibility counts.
It demonstrates the mismatch-diagnosis stage but does not claim to rerun every
original raster, computer-vision, API, LLM, geocoding or GIS operation.
