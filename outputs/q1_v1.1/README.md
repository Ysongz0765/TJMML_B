# Q1 v1.1

This directory is a new result set. `frozen/v1.0/` is read-only and is hash-checked before and after the run.

Run from the repository root:

```powershell
$env:Q1_V11_BOOTSTRAP_B = "2000"
python -m src.q1.run_q1_v11
```

The main machine-readable result is `results_summary_v1.1.json`. Excel workbooks are in `tables/`, figures in `figures/`, Bootstrap details in `bootstrap/`, and method/QC reports in `diagnostics/`.

The current result is not ready to freeze because GLM-5.2 C5 applicability still requires manual confirmation. Its C5 score remains NA and its Ranking-A result is reported only as a conditional interval.
