# Final vs Provisional Audit

Audit date: 2026-08-17

## Decision

`FINAL_VS_PROVISIONAL_AUDIT = NOT_RUN`

There is no valid final human-verified result set to compare with the
provisional outputs. The final runner stopped at the human-verification gate
because all three pricing verification files still contain 0/10 TRUE rows.
This report records the required comparison fields so they can be populated
after the P0 gate is closed.

| Item | Final result | Comparison |
|---|---|---|
| Costs | NOT RUN | `max absolute change` and `max relative change` require a final cost table. |
| Pareto membership | NOT RUN | New entrants and exits cannot be assessed. |
| Budget switches | NOT RUN | Threshold changes cannot be assessed. |
| ICER | NOT RUN | Numeric changes cannot be assessed. |
| Fit selection | NOT RUN | AICc/LOOCV selection changes cannot be assessed. |
| Sensitivity conclusion | NOT RUN | Final-price sensitivity cannot be assessed. |

The pre-final baseline is the provisional output set from commit `441f935`.
No price values were changed during this blocked audit.
