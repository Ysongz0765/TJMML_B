# Stability audit

## Finding
The v1.0 implementation min-max normalized each bootstrap BT fit to 0-100 and used the median model-level score SD. More importantly, it resampled Exact Settings only within each Benchmark Family while forcing every Family to remain present. C2, C3 and C5 contain only single-setting Families, so those dimensions were reproduced identically in all 2,000 iterations. Their median SD was exactly zero and T=1 followed mechanically. This is normalization/resampling pseudo-stability, not evidence of robustness to alternative benchmarks or sources.

## v1.1 definition
For each dimension, v1.1 fits the main regularized BT model, simulates the pairwise outcomes under the fitted BT probabilities while retaining the frozen settings, margins, family balancing and applicability structure, and refits the raw latent abilities theta. Stability is T_d=(1+median_b rho_d^b)/2, where rho is Spearman correlation between bootstrap and main theta rankings. No per-iteration min-max score is used in T_d.

## Interpretation boundary
T_d measures latent-ranking repeatability conditional on the frozen benchmark universe, fixed sources and fixed capability applicability. LOFO and LOSO, rather than Bootstrap, assess structural dependence on a Benchmark Family or source.

| dimension | old_median_score_sd | old_unique_bootstrap_score_vectors | old_median_endpoint_frequency | audit_conclusion |
| --- | --- | --- | --- | --- |
| C1 | 13.94593249460011 | 94 | 0.037 | VARIATION_PRESENT |
| C2 | 0.0 | 1 | 0.0 | PSEUDO_STABLE_RESAMPLING_DEGENERACY |
| C3 | 0.0 | 1 | 0.0 | PSEUDO_STABLE_RESAMPLING_DEGENERACY |
| C4 | 2.2514209782704304 | 681 | 0.0 | VARIATION_PRESENT |
| C5 | 0.0 | 1 | 0.0 | PSEUDO_STABLE_RESAMPLING_DEGENERACY |

| perspective_dimension | valid_bootstrap_replicates | median_spearman_theta_rank | latent_ranking_stability_T | perspective |
| --- | --- | --- | --- | --- |
| C1 | 2000 | 0.13333333333333333 | 0.5666666666666667 | A |
| C2 | 2000 | 0.2333333333333333 | 0.6166666666666667 | A |
| C3 | 2000 | 0.2333333333333333 | 0.6166666666666667 | A |
| C4 | 2000 | 0.09999999999999999 | 0.55 | A |
| C5 | 2000 | 0.1785714285714286 | 0.5892857142857143 | A |
| C1 | 2000 | 0.1515151515151515 | 0.5757575757575757 | B |
| C2 | 2000 | 0.23636363636363633 | 0.6181818181818182 | B |
| C3 | 2000 | 0.19999999999999998 | 0.6 | B |
| C4 | 2000 | 0.12727272727272726 | 0.5636363636363636 | B |
| C1 | 2000 | 0.07142857142857144 | 0.5357142857142857 | C |
| C2 | 2000 | 0.21428571428571433 | 0.6071428571428572 | C |
| C3 | 2000 | 0.10714285714285716 | 0.5535714285714286 | C |
| C4 | 2000 | 0.1785714285714286 | 0.5892857142857143 | C |
| C5 | 2000 | 0.1785714285714286 | 0.5892857142857143 | C |
