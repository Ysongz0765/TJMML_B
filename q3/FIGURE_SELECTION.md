# Q3 Figure Selection

Selection status: based on the regenerated final output set from the
8-model FULL, human-verified main cohort.

The PNG and PDF files with the same stem are one logical figure in two export
formats, not two separate paper figure numbers.

## MAIN_TEXT

| Figure group | Files | Main message | Paper section |
|---|---|---|---|
| Cost--utility/Pareto | `q3/outputs/figures/q3_cost_utility_{Research,General,Coding}.{png,pdf}` | Scenario-specific cost and utility trade-offs; no global best model. | Results: Pareto |
| Budget steps | `q3/outputs/figures/q3_budget_steps_{Research,General,Coding}.{png,pdf}` | Actual budget thresholds and selected model after each threshold. | Results: Budget selection |
| ICER | `q3/outputs/figures/q3_icer_{Research,General,Coding}.{png,pdf}` | Marginal cost per utility gain along each frontier. | Results: ICER |
| Output/input ratio | `q3/outputs/figures/q3_ratio_sensitivity_{Research,General,Coding}.{png,pdf}` | How output-heavy workloads alter cost/Pareto structure. | Sensitivity |
| Bootstrap Pareto probability | `q3/outputs/figures/q3_pareto_probability_{Research,General,Coding}.{png,pdf}` | Utility-bootstrap uncertainty in frontier membership. | Robustness |

## APPENDIX

| Figure group | Files | Reason |
|---|---|---|
| Cost--performance fits | `q3/outputs/figures/q3_cost_performance_fit_{Research,General,Coding}.{png,pdf}` | Useful diagnostics, but small frontier samples and fit warnings limit main-text interpretation. |
| Price perturbation | `q3/outputs/figures/q3_price_perturbation_{Research,General,Coding}.{png,pdf}` | Complements the main sensitivity result without repeating the nominal frontier. |

## DIAGNOSTIC_ONLY

No separate diagnostic-only figure files were generated. Fit warnings,
small-sample caveats, and validation details are reported in the tabular
diagnostics and audit documents rather than promoted to figures.
