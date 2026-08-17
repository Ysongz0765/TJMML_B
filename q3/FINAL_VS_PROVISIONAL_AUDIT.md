# Final vs Provisional Audit

Audit date: 2026-08-17

## Decision

`PROVISIONAL_TO_FINAL_NUMERIC_CHANGE = NONE`

The final runner was executed after the eight FULL rows were marked
`VERIFIED_FULL_PRICE`. Human review changed only audit/provenance fields; it did
not change any price number, utility value, workload, or model mapping.

| Item | Final result | Comparison |
|---|---|---|
| Costs | PASS | Maximum absolute change = 0.0 USD; maximum relative change = 0.0. |
| Pareto membership | PASS | No entrants or exits. |
| Budget switches | PASS | Thresholds and model sequences unchanged. |
| ICER | PASS | All 9 rows unchanged. |
| Fit selection | PASS | All 16 fit rows unchanged. |
| Sensitivity conclusion | PASS | All 504 sensitivity rows unchanged. |
| Bootstrap Pareto | PASS | All 24 probabilities unchanged. |

The pre-final baseline is the provisional output set from commit `441f935`.
The final output set is generated from the same numerical inputs with the
verified FULL cohort gate applied.
