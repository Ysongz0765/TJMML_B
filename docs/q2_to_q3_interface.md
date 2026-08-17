# Q2 to Q3 continuous scene-utility interface

## Interface

- File: `q2/q3_handoff/q2_to_q3_scene_utility.csv`
- Rows: 10, one per frozen Q1/Q2 model identity.
- Q1 freeze: `frozen/v1.0 + Q1 v1.2 official outputs`.
- Q2 freeze: `Q2_FINAL_v1.0`.
- Q2 model-spec SHA-256: `5eb483577f32621802c3249d6a39fbdf81e8170fa6e1f7af2cf381fd3135482d`.

## Performance variables for Q3

Q3 should use the continuous Q2 CES utilities:

- `research_utility`
- `dialogue_utility`
- `coding_utility`

as the scenario-specific performance variables. Q3 must perform cost-performance and Pareto calculations separately by scenario because the three CES utilities use different core dimensions, weights and substitution parameters.

The corresponding `_utility_low` and `_utility_high` columns are the 95% intervals from Q1 latent-ability uncertainty propagation. `_top1_probability` and `_top3_probability` are explanatory uncertainty measures.

## Rank usage rule

`research_rank`, `dialogue_rank` and `coding_rank` are ordinal variables. Rank does not preserve the size of performance gaps and must not be inserted directly into a numerical performance-cost function. The continuous CES utility preserves the modeled within-scene performance distance and is therefore the Q3 performance-benefit input. Rank may be used only for reporting and interpretation.

Q3 must not replace the Q2 utility with Q1 overall score, a rank-to-score conversion, a benchmark score, or a newly reweighted composite performance index.
