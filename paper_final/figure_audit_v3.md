# Figure Audit v3

## Scope

This audit checks the figures used by `final_paper_v3.pdf` against the
requested visual sequence, the formal Q1--Q3 outputs, the manuscript captions,
and the unified style source. No frozen data file was edited.

## Main-figure audit

| Figure | Current form | Information carried | Source / consistency check |
| --- | --- | --- | --- |
| 1 | User-provided framework image | Public evaluations → five-dimensional ability → scene utility → budget decision | `fig_framework_user.jpg`; used in the problem-analysis section |
| 2 | Coverage heatmap with C1--C5 grouping | observed, ordinary missing, and evidence-supported structural NA | `final_modeling_matrix_v1.0.csv`; short Benchmark labels retained |
| 3 | Missing-aware correlation matrix | lower triangle \(\rho_{ab}\), upper triangle Common-N | `spearman_missing_aware.xlsx`; small Common-N values are left visually restrained |
| 4 | Radar + horizontal bar with Bootstrap CI | five-dimensional profile and Ranking A center estimate with interval uncertainty | Q1 capability scores and formal Bootstrap workbook |
| 5 | Horizontal violin + box + point estimate | Bootstrap rank distribution, IQR/median, and Ranking A point rank | `bootstrap_ranking_A_v1.2.csv`; full probability matrix moved to appendix |
| 6 | Enhanced dot-range / lollipop | LOFO rank correlation by Benchmark Family; \(\rho=0.95\) reference and disconnected-network marker | `lofo_summary_v1.2.csv`; disconnected cases are labeled rather than left blank |
| 7 | Scenario-weight heatmap | Research / General / Coding weights on C1--C5 | Q2→Q3 formal interface; unused dimensions shown as `—` |
| 8 | Scenario utility ranking matrix | within-scenario relative utility colors and three-decimal formal utility labels | `scenario_utility.csv`; each column is normalized separately |
| 9 | Bump chart | Ranking A → Research → General → Coding rank migration | Formal Q1 and Q2 ranking outputs; five or fewer models emphasized and others faded |
| 10 | CES rank-stability heatmap | rank under tested \(\rho\) values for Research and Coding; formal \(\rho\) marked | Formal Q2 sensitivity output; rank, not cross-scene utility, is encoded |
| 11 | Horizontal stacked bars | input and output workload cost components and total cost | `scenario_costs_final.csv`; sorted by total cost |
| 12 | Pareto scatter panels | utility--cost trade-off in Research, General, Coding | `pareto_results_final.csv`; frontier and dominated points distinguished |
| 13 | Budget decision bands | continuous budget intervals and formal switching thresholds | `budget_switch_points_final.csv`; the legacy filename `fig_q3_budget_steps` contains the new band design |

## Style audit

- Single source: `scripts/plotting/style.py`.
- Required colors are defined in `PALETTE`, with model and status mappings in
  `MODEL_STYLE` and `STATUS_STYLE`.
- Main colors used: mist blue `#8DB3D0`, cream `#E5DABC`, sage
  `#C0D7BE`, ice blue `#DCE9ED`, and neutral gray.
- No manuscript figure uses Matplotlib `tab10`, `rainbow`, `jet`, or a
  saturated red/orange/purple default.
- Figure artifacts were validated by
  `scripts/plotting/validate.py`: 15 non-empty figure stems, each with PDF,
  SVG, and PNG outputs; main figures meet the minimum preview dimensions.

## Figure-text gates

- Every main figure has a preceding motivation or interpretation paragraph.
- Every figure caption identifies the encoded quantity and the comparison
  scope.
- Figure 5 no longer describes a probability heatmap in the正文; that matrix
  is explicitly appendix-only.
- Figure 6 distinguishes LOFO structural robustness from Bootstrap rank
  uncertainty.
- Figure 8 explicitly warns that colors are not cross-scenario absolute
  utility comparisons.
- Figure 10 describes rank stability rather than old utility curves.
- Figure 13 is interpreted as a budget recommendation rule rather than a
  generic cost-growth curve.

## Visual QA

- `final_paper_v3.pdf` compiled to 18 pages.
- All 18 pages were rendered to `paper_final/rendered_v3_final/`.
- Pages 1, 6, 10, 15, and 18 were visually inspected after the final
  compilation; no clipping, blank figure, or figure-caption mismatch was
  found.
- Remaining LaTeX messages are non-fatal `Underfull \hbox` warnings in long
  reference and price-configuration lines.

## Status

**PASS.** The visual narrative is now:

`framework → coverage → correlation → capability/ranking → uncertainty → LOFO → scenario weights → scenario utility → rank migration → CES stability → cost → Pareto → budget bands`.

