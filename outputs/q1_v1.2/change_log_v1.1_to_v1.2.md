# Change log: Q1 v1.1 to Q1 v1.2

1. Retained all v1.1 method corrections and frozen benchmark inputs.
2. Added manual_capability_verification_v1.2.xlsx; GLM-5.2 is human-confirmed Type A structural capability absence.
3. Type A set is now DeepSeek-V4-Pro Max, DeepSeek-V4-Flash Max and GLM-5.2; raw benchmark NA cells remain unchanged.
4. Ranking A now includes all ten models with C5* = A_i S_i5^BT; Type-A C5* values are 0 only in the composite system.
5. Recomputed Information, Redundancy, latent ranking stability, weights, rankings, Bootstrap, LOFO, LOSO and sensitivity analyses.
6. Ranking C is renamed to the subset with estimable C5 multimodal ability.
7. Kimi ranks A/B/C are 3/2/3 after the ten-model rerun.
8. Kimi strongest/weakest gaps are now C4 (+36.415) and C5 (-20.513).
9. Table 3 coverage: corrected by reading frozen manifest model_coverage; the Boolean selection indicator is renamed '进入正式模型'. An equality assertion now compares table 2 and table 3 coverage.
10. Source analysis: added formal source table and Leave-One-Source-Out diagnostics.
11. Retained conclusions: regularized BT, five dimensions, Family balancing, and Kimi's strong C4 evidence remain.
12. Modified conclusions: C3 remains model-inferred with weaker direct evidence than C4; C5 gap is compared only with the seven-model estimable-C5 subset.

Q1_V1.2_READY_TO_FREEZE = TRUE
