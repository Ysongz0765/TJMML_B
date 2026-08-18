# Language Audit v3

## Audit target

The manuscript was checked for a national mathematical-modeling-contest
style: each section begins from the problem requirement, motivates the
mathematical choice, interprets results as phenomenon → cause → implication,
and keeps engineering traceability in the appendix or source notes.

## Completed checks

- Abstract begins from the contest's model-evaluation and scene-selection
  problem, then follows Q1 → Q2 → Q3.
- Problem restatement uses “题目要求 + 数学化转译” for all three questions.
- Q1 begins with the cost of direct averaging, zero-imputation, and complete
  case deletion; it explains why missingness must remain semantic.
- Q2 begins by explaining why an overall ranking cannot answer scene choice;
  CES is motivated by incomplete substitution and shortfall effects.
- Q3 begins by explaining why scene utility cannot determine deployment;
  workload cost, rather than API unit price alone, is introduced.
- Q1 results distinguish point estimates from Bootstrap uncertainty.
- LOFO is explicitly limited to single-Benchmark structural robustness.
- Q2 rank migration is explained as demand mapping, not as a contradiction in
  the overall ranking.
- Q3 results distinguish utility, cost observability, Pareto efficiency, and
  budget feasibility.
- The conclusion gives decision rules for overall ability, research tasks,
  coding tasks, cost-sensitive selection, and higher budgets.

## Terminology audit

The following engineering-heavy expressions were removed from the正文:

`frozen interface`, `bootstrap_id`, `FULL cohort`, `official output`,
`pricing audit`, and `comparison graph disconnected`.

The remaining technical terms are retained only where they are mathematical
objects or necessary source-trace labels, for example `Benchmark Family`,
`Exact Setting`, `CES`, and `LOFO`. Price snapshots and configuration strings
remain in the appendix because they document reproducibility rather than carry
the main argument.

## Claim discipline

- No claim says that Bootstrap makes the first three ranks “stable”.
- No missing price is imputed.
- No structural NA is treated as score zero.
- No cross-scenario comparison of raw CES utility is asserted.
- No result is described as “significant” without a statistical test.
- Formal numerical outputs are unchanged: Q1 coverage, Ranking A scores,
  Q2 scene winners, Bootstrap Top-3 probability, and Q3 budget thresholds
  remain the registered values.

## Residual language notes

- English model and benchmark names are preserved for registry consistency.
- The appendix necessarily contains source-oriented terms such as SKU,
  configuration, and frozen snapshot date.
- References contain official-source labels and URLs by design.

## Status

**PASS.** The正文 reads as a problem-driven mathematical-modeling paper;
remaining audit terminology is confined to reproducibility material.

