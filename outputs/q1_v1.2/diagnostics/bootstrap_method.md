# Bootstrap method (Q1 v1.2)

1. Resampling unit: one weighted pairwise comparison outcome in the regularized BT likelihood (parametric Bernoulli draw under the main fitted BT probability).
2. Benchmark Family sampling: the frozen Family universe is fixed; no Family is resampled or substituted.
3. Single-setting Family: retained and its pairwise outcomes are simulated, avoiding the v1.0 deterministic-setting degeneracy.
4. Family absence: not allowed in Bootstrap; structural absence is evaluated by LOFO/LOSO.
5. Pairwise relation: y is regenerated from the main BT probability; frozen margins and family-balanced weights are retained.
6. BT refit: yes, for every dimension and every replicate.
7. Dimension weights: I and R are recomputed in every replicate; the independently estimated latent-rank T is held fixed to avoid a nested Bootstrap.
8. Network disconnection: impossible under the fixed pairwise edge set; nevertheless every replicate is checked.
9. BT non-convergence: the run fails and is not silently discarded.
10. Random seed: 20260817.
11. 95% CI: empirical percentile interval (2.5%, 97.5%).
12. C5 capability absence: Type-A availability zeros are fixed after BT fitting and are never simulated as benchmark scores; all ten models are included in deterministic Ranking A.

Under the fixed Benchmark set, source structure and model capability applicability, Kimi K3's empirical Top-3 frequency in 2000 Bootstrap replicates is 0.422.
