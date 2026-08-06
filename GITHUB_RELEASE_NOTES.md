# GitHub release notes

## Scientific-alignment revision

This version corrects the executable repository so its formulas, terminology and
claims follow the thesis evidence boundary.

### Corrected

- removed the synthetic SMI number from the application homepage;
- labels any computed SMI as an output of the currently loaded synthetic table;
- separates raw non-negative visibility `R_i` from its log-z standardised form;
- computes SMI only from raw spatial shares;
- computes SR from log-transformed z-scores;
- min-max rescales `|SR|` to `[0, 1]`;
- removes the unsupported `±0.25` directional threshold;
- removes automated per-cell planning prescriptions based on arbitrary cut-offs;
- aligns the LLM schema with the thesis-core fields while labelling audit
  additions separately;
- renames the generated output to `synthetic_demo_mismatch_result.csv`;
- strengthens formula-level tests and evidence-boundary documentation.

### Evidence boundary

The repository is a reproducible diagnostic prototype using synthetic,
thesis-aligned inputs. It does not claim to recreate every original empirical
map or the complete end-to-end CV–LLM processing archive.
