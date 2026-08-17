# Q3 Stage Report

Audit date: 2026-08-17

Q3_FRAMEWORK_READY = TRUE
Q3_PRICING_MAPPING_READY = TRUE
Q3_PRICING_DATA_READY = FALSE
Q3_PRICING_HUMAN_VERIFIED = FALSE
Q3_WORKLOAD_BASELINE_READY = TRUE
Q2_FORMAL_SCENARIO_UTILITY_FOUND = TRUE
Q2_SCENARIO_UTILITY_VALIDATED = TRUE
Q2_BOOTSTRAP_UTILITY_FOUND = TRUE
Q3_READY_FOR_FINAL_RUN = TRUE
Q3_PRICING_HUMAN_VERIFIED = FALSE
Q3_MAIN_ANALYSIS_COHORT_READY = FALSE
Q3_PROVISIONAL_RESULTS_READY = TRUE
Q3_FINAL_HUMAN_VERIFIED_RESULTS_READY = FALSE
Q3_FINAL_RESULTS_READY = FALSE
Q3_READY_TO_FREEZE = FALSE
Q3_FROZEN = FALSE
Q3_REPRODUCIBILITY_AUDIT = NOT_RUN
Q3_PAPER_CONSISTENCY_AUDIT = NOT_RUN
Q3_FINAL_P0_COUNT = 1
Q3_FINAL_P1_COUNT = 2

## Current State

- Formal Q2 scenario utility and bootstrap utility were synchronized from
  `origin/q2-final-paper` at commit `bff0e185510f79bd78dd190ccedc47c81b12f137`.
- The nominal interface contains 30 rows: 10 models x 3 scenarios. The bootstrap
  interface contains 60,000 rows from 2,000 draws. All automated Q2-to-Q3
  interface checks passed.
- Eight models have complete observable base costs, but the strict formal main
  cohort is currently empty because no pricing row has passed the three-file
  human-verification gate.
- Claude Fable 5 is retained as `PARTIAL` because its fallback configuration
  cost is unresolved. GLM-5.2 is retained as `MISSING` because an official
  public input/output API price was not observable. Neither row is imputed or
  included in the main Pareto analysis.
- All pricing rows remain `human_verified=FALSE`; therefore the result package
  is provisional and is not the final human-verified release. See
  `FINAL_INPUT_AUDIT.md` and `Q3_FINAL_AUDIT.md`.

## Generated Results

The previous provisional run generated 24 FULL-cohort cost-utility rows, 24
budget rows, 9 ICER rows, 16 fit rows, 504 sensitivity rows, 24 bootstrap
Pareto-probability rows, and 42 PNG/PDF figures. They remain historical
provisional outputs; the final human-verified rerun is blocked by P0-1.
See `Q3_RESULTS_REPORT.md` for the interpretation and exact provisional
scenario-level results.

## Readiness Logic

`Q3_READY_FOR_FINAL_RUN` means that the formal Q2 utility interface, workload
baseline, and a transparent FULL cost cohort are available. It does not mean
that every model has an observable complete price or that human verification is
complete.
