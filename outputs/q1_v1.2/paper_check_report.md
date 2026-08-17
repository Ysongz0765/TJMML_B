# Q1 v1.2 paper and consistency check

## Content check

- Ranking A contains 10 models and uses one unified C1--C5* score system.
- Ranking B contains 10 models and uses recomputed C1--C4 weights.
- Ranking C contains 7 models and is named “具有可估计 C5 能力的多模态模型子集评价”.
- GLM-5.2 is recorded as `multimodal_capable = FALSE`, Type A, with manual evidence; no unresolved applicability remains.
- Ranking A tables label the derived column `C5* 多模态有效能力`; Type A values are displayed as `0*`.
- Raw C5 Benchmark observations remain missing for GLM; no missing Benchmark value was converted to a raw score of zero.
- Kimi values in the paper are from `results_summary_v1.2.json`: A/B/C rank `3/2/3`, A score `53.720`, C4 gap `+36.415`, C5 gap `-20.513`, Bootstrap Top-3 `0.4225`.
- Data sources represented in the正文 table include LiveBench, Artificial Analysis, official technical reports/model materials, Kimi materials and OpenRouter.
- Stability uses $T_d=(1+\operatorname{median}_b\rho_d^{(b)})/2$ based on BT latent rankings.
- LOFO and LOSO are separately described; disconnected networks are treated as structural identifiability results.

## LaTeX check

- Independent PDF: `outputs/q1_v1.2/main_q1_v1_2.pdf`.
- Independent paper-folder PDF: `outputs/q1_v1.2/paper_q1_v1_2/main_q1_v1_2.pdf`.
- Final page count: 8.
- Figures used: flow, coverage, Family Spearman, five-dimensional scores, Ranking A Bootstrap CI, LOFO, and Kimi gap.
- Tables used: data sources, objective weights, Ranking A; supporting Ranking B/C and robustness tables are in the output workbooks.
- Both independent builds were run twice with XeLaTeX.
- No undefined references, missing figures, fatal errors, Overfull/Underfull boxes, or Float-too-large messages were found in the final logs.
- Visual page inspection found readable figures, stable tables, no clipping, and no large blank float pages.

## Numerical consistency

| Check | Result |
| --- | --- |
| Frozen SHA-256 unchanged | PASS; 16 checksum entries matched |
| Main / Bootstrap BT convergence | PASS |
| Ranking A/B/C model counts | PASS; 10 / 10 / 7 |
| Weight sums A/B/C | PASS; 1 / 1 / 1 |
| Bootstrap replicates | PASS; 2000 |
| C5* versus raw C5 distinction | PASS |
| Tables, JSON and manuscript key values | PASS |
| Unresolved applicability | PASS; none |

## Freeze gate

`Q1_V1.2_READY_TO_FREEZE = TRUE`
