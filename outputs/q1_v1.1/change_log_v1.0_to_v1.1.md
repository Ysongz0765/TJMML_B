# Change log: Q1 v1.0 to Q1 v1.1

1. C5 missingness: split into Type A structural capability absence, Type C normal observation, and REQUIRES_MANUAL_CONFIRMATION.
2. Capability absence: DeepSeek-V4-Pro Max and DeepSeek-V4-Flash Max, supported by the official DeepSeek-V4 report.
3. Benchmark missing/manual confirmation: GLM-5.2 cannot be classified from frozen evidence and remains NA; no zero is assigned.
4. Stability: replaced min-max score-SD stability with raw BT-theta latent ranking stability.
5. New weights: see results_summary_v1.1.json and paper_table_q1_v11_dimension_weights.xlsx; A/B/C weights are separately recomputed.
6. Ranking: replaced one missing-aware-renormalized list with Ranking A, Ranking B and Ranking C.
7. Kimi ranks A/B/C are 3/2/3; v1.0 rank was 3.
8. Kimi strongest/weakest gaps are now C4 (+31.707) and C5 (-20.513).
9. Table 3 coverage: corrected by reading frozen manifest model_coverage; the Boolean selection indicator is renamed '进入正式模型'. An equality assertion now compares table 2 and table 3 coverage.
10. Source analysis: added formal source table and Leave-One-Source-Out diagnostics.
11. Retained conclusions: regularized BT, five dimensions, Family balancing, and Kimi's strong C4 evidence remain.
12. Modified conclusions: v1.0 overall scores/weights/Top-3 wording are not carried forward; C3 is explicitly moderate model-inferred evidence, and Ranking A is conditional on resolving GLM C5 applicability.

Q1_V1.1_READY_TO_FREEZE = FALSE
