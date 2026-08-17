# Q2 final outputs — frozen formal results

These files were generated only after the standardized Q1 v1.2 inputs passed the
official Q2 validation guard.  They are the machine-readable source for the Q2
paper tables, figures, rankings, robustness analysis, and uncertainty summary.

The direct Q2-to-Q3 performance interface is exported separately under
`q2/outputs/`:

- `scenario_utility.csv` — 30 nominal KL-CES scene utilities;
- `scenario_utility_summary.csv` — the same results ordered within scene;
- `scenario_utility_bootstrap.csv` — 2000 aligned Q1-uncertainty propagation draws;
- `q2_to_q3_validation.csv` — interface data-quality checks.

The interface contract is `q2/metadata/q2_to_q3_interface.md`.  Q1 frozen data
remain read-only and are not rewritten by the Q2 runner.
