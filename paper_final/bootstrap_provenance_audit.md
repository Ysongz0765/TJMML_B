# Bootstrap Provenance Audit

## Source lineage

- Source branch: `origin/q2-final-paper`
- Source commit: `bff0e185510f79bd78dd190ccedc47c81b12f137`
- Sync date: `2026-08-17`
- Frozen source files and SHA-256 match:
  - `q2/outputs/scenario_utility_bootstrap.csv`
  - `q2/outputs/scenario_utility.csv`
  - `q2/outputs/scenario_utility_summary.csv`
  - `q2/outputs/q2_to_q3_validation.csv`
  - `q2/metadata/q2_to_q3_interface.md`

## Structural checks

- Rows: `60000`
- Bootstrap draws: `2000`
- Models: `10`
- Scenarios: `Research`, `General`, `Coding`
- Rows per draw: `30` exactly
- Unique models per draw: `10` exactly
- Unique scenarios per draw: `3` exactly
- Duplicate key rows on `(bootstrap_id, model_id, scenario)`: `0`
- Missing utility values: `0`
- Non-finite utility values: `0`

## Provenance notes

- `bootstrap_id` is the aligned draw index used by the frozen Q2 interface.
- `source_bootstrap_id` records the upstream Q1 normal-approximation draw identifier `q1_uncertainty_normal_approx_####`.
- The table is treated as read-only by downstream Q3 code.
- Q3 does not regenerate the bootstrap table; it only validates row counts and uses the frozen utilities for Pareto probability calculations.

## Code-level audit

- `src/q1/run_q1_v12.py` generates the Q1 bootstrap via parametric Bernoulli resampling under the fitted BT probabilities, then refits the latent model 2,000 times.
- `q2/outputs/scenario_utility_bootstrap.csv` does not preserve the original joint Q1 bootstrap table; it stores 2,000 aligned Q2 utility draws produced from the Q1 point estimates plus dimension-level bootstrap standard deviations under an independent normal approximation.
- `q3/src/run_q3.py` validates that the bootstrap file has `60000` rows, `2000` draws, no duplicates, no missing utilities, and exactly the three expected scenarios.
- `q3/src/sync_q2_inputs.py` copies the bootstrap file byte-for-byte from `origin/q2-final-paper`.
- `scripts/plotting/q2_figures.py` reads the frozen interface and now uses the Q2 latent-strength scale for rho sensitivity.

## Conclusion

The bootstrap interface is internally consistent and provenance-complete for paper use. No bootstrap values were rewritten during the paper integration step.
