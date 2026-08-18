# Paper Audit v2

## Gate status

- Gate 1: PASS
- Gate 2: PASS
- Gate 3: PASS
- Gate 4: PASS
- Gate 5: PASS
- Gate 6: PASS
- Gate 7: PASS
- Gate 8: PASS
- Gate 9: PASS
- Gate 10: PASS

## Build status

- Final PDF built: `paper_final/main.pdf`
- Copied deliverables: `paper_final/final_paper_v2.pdf`, `paper_final/final_paper.pdf`
- Page count: 15
- PDF validation: rendered pages checked on pages 1, 6, 10, 14, 15

## Key conclusions and sources

1. Q1 coverage 164/210 = 78.1% from `frozen/v1.0/final_modeling_matrix_v1.0.csv`.
2. Q1 Ranking A top three are GPT-5.6 Sol, Claude Fable 5, and Kimi K3 from `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx`.
3. Q1 bootstrap provenance is documented in `paper_final/bootstrap_provenance_audit.md`.
4. Q2 scenario weights and nominal utilities are read from `q3/data/q2_to_q3_interface.md` and `q3/frozen/v1.0/scenario_utility.csv`.
5. Q3 Pareto and budget thresholds are read from `q3/frozen/v1.0/pareto_results_final.csv` and `q3/frozen/v1.0/budget_switch_points_final.csv`.

## Figure audit summary

- Q1 core figure updated to radar + horizontal bar with Bootstrap CI.
- Q1 core figure image was replaced with a tighter crop of the provided screenshot so the manuscript figure no longer carries the embedded caption block.
- Q1 auxiliary figures updated for short labels, Common-N annotation, visible rank probabilities, and disconnected LOFO markers.
- Q2 split into separate weight-matrix and utility-panel figures.
- Q3 Pareto panels fixed in Research | General | Coding order.
- Q3 workload curve removed from the manuscript and replaced by budget-step decision figure.

## Residual notes

- No frozen file was modified.
- Appendix tables are narrower than the earlier draft, but some long configuration strings still wrap inside the price snapshot table.
- Remaining LaTeX warnings are non-fatal and do not block the PDF.
