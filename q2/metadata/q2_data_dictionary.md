# Q2 data dictionary

| field | meaning | unit/range | missing-value meaning | source file | Q2 intended use |
| --- | --- | --- | --- | --- | --- |
| model_id | Stable machine-readable model id | text | not allowed | all data files | joins across Q2 inputs |
| model | Human-readable model name | text | not allowed | all data files | reporting and sanity checks |
| C1_score | Q1 0-100 BT score for complex reasoning | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C2_score | Q1 0-100 BT score for knowledge/factual reliability | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C3_score | Q1 0-100 BT score for long context | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C4_score | Q1 0-100 BT score for code/software engineering | 0-100 | unavailable only if BT cannot estimate | q1_capability_scores.csv | capability profile |
| C5_BT_score | Q1 0-100 BT score for estimable multimodal ability | 0-100 | structural C5 absence or not estimable; not benchmark zero | q1_capability_scores.csv | capability profile when C5 is estimable |
| C5_effective_score | Q1 Ranking A effective C5* availability score | 0-100 | not expected | q1_capability_scores.csv | capability availability for Q1-style all-model comparison |
| C1_theta-C5_theta | Raw regularized Bradley-Terry latent ability | real-valued theta | dimension not estimable; never auto-fill with 0 | q1_bt_latent_scores.csv | alternative modeling input without min-max scaling |
| multimodal_capable | Whether model has native multimodal capability under Q1 definition | TRUE/FALSE | not expected | q1_model_applicability.csv | C5 applicability gating |
| C5_status | C5 applicability status | ESTIMABLE / STRUCTURAL_CAPABILITY_ABSENCE / BENCHMARK_MISSING | not expected | q1_model_applicability.csv | capability applicability handling |
| C5_direct_benchmark_count | Number of direct selected C5 benchmark observations | integer | 0 means no direct C5 observation | q1_model_applicability.csv | evidence coverage |
| C3_direct_observation_strength | Rule-based coverage note for C3 | text category plus note | unavailable if no diagnostic support | q1_model_applicability.csv | caution for long-context scenario |
| C4_direct_observation_strength | Rule-based coverage note for C4 | text category plus note | unavailable if no diagnostic support | q1_model_applicability.csv | caution for coding scenario |
| ranking_A_rank / ranking_A_score | Q1 all-model C1-C5* reference rank and score | rank / 0-100 composite | not expected | q1_model_rankings.csv | reference sanity check only |
| ranking_B_rank / ranking_B_score | Q1 all-model C1-C4 reference rank and score | rank / 0-100 composite | not expected | q1_model_rankings.csv | reference sanity check only |
| ranking_C_rank / ranking_C_score | Q1 estimable-C5 subset reference rank and score | rank / 0-100 composite | NA for non-Ranking-C models | q1_model_rankings.csv | reference sanity check only |
| theta_bootstrap_mean / theta_bootstrap_sd | Bootstrap mean and SD of raw BT theta | theta | unavailable for ranking-level rows | q1_uncertainty.csv | uncertainty-aware modeling |
| score_bootstrap_mean / score_bootstrap_sd | Bootstrap mean and SD of dimension or ranking score | 0-100 | unavailable for stability-only rows | q1_uncertainty.csv | uncertainty-aware modeling |
| score_ci_low / score_ci_high | Percentile 95% bootstrap interval for score | 0-100 | unavailable when Q1 did not define a score row | q1_uncertainty.csv | uncertainty bounds |
| rank_ci_low / rank_ci_high | Percentile 95% bootstrap interval for Q1 ranking | rank | unavailable for dimension score rows | q1_uncertainty.csv | ranking uncertainty reference |
| T_d | Q1 v1.2 latent-ranking stability | 0-1 | unavailable for model-only rows where not applicable | q1_uncertainty.csv and q1_dimension_weights_reference.csv | data reliability cue |
| q1_weight | Q1 Ranking A objective weight | sums to 1 | not expected | q1_dimension_weights_reference.csv | reference only, not scenario weight |
| information / redundancy / stability | Q1 weight components | non-negative | not expected | q1_dimension_weights_reference.csv | audit and reference |
| direct_observation_count | Count of selected direct benchmark rows observed | integer | 0 means no direct observation | q1_evidence_strength.csv | evidence coverage |
| benchmark_family_count | Count of benchmark families directly observed | integer | 0 means no direct family | q1_evidence_strength.csv | evidence coverage |
| source_count | Count of source ids directly observed | integer | 0 means no direct source | q1_evidence_strength.csv | source diversity cue |
| evidence_strength | Rule-based category, not an arbitrary score | HIGH / MEDIUM / LOW | not expected | q1_evidence_strength.csv | scenario-risk adjustment candidate |

Important C5 distinction: `C5_BT_score = NA` and `C5_effective_score = 0` can occur at the same time. This means the model lacks native multimodal capability under Q1's definition; it does not mean the model received a raw benchmark score of 0.
