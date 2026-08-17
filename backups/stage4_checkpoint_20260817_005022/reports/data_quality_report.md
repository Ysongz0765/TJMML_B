# Data Quality Report - Phase 3

## A. 数据规模

- RawData records: 242 (209 inherited + 33 Phase3 evidence records)
- Core model versions: 10
- Exact settings in Final Modeling Matrix: 21
- Benchmark Families: 14
- Selected nonempty matrix cells: 164 / 210
- Overall coverage: 78.10%

## B. 来源质量

- Raw source-authority counts: Level A 116; Level B 103; Level C 23
- Final-matrix source-authority counts: Level A 116; Level B 25; Level C 23
- LiveBench cell share: 60.98% overall; 86.21% in C1; 78.13% in C4
- Source IDs registered: 19; every selected numeric record has a URL and source ID

Artificial Analysis is Level A only for its own AA-LCR/AA-Omniscience
benchmarks. Its HLE and MMMU-Pro re-evaluations are Level C independent-platform
sources and remain Grade B comparable evidence.

## C. 缺失情况

- Overall missing rate: 21.90%
- Minimum core-model coverage: 66.67% (Qwen3.8-Max)
- Kimi K3 coverage: 85.71%
- C5 is complete only for the seven multimodal-applicable core models; no score
  is imputed for text-only models.

## D. 可比性与网络

- Final matrix uses Grade A/B records only.
- C1-C5 eligible-model largest connected component ratio: 100% in every dimension.
- C5 all-core ratio is 70% because three text-only models are explicitly out of
  scope for multimodal BT rather than assigned zero or fabricated scores.
- C3 becomes severely disconnected if SRC014 (AA-LCR) is removed and is marked
  `FRAGILE_CONNECTED`.

## E. 冲突与验证

- Strict same-model + same-version + same-metric + same-setting conflict groups: 0
- Matrix lineage coverage: 164 / 164 nonempty cells (100%)
- Human-verified records: 0 / 164
- Exact-protocol independent cross-validation remains below the 20%-30% soft
  target; repeated vendor citations were not misclassified as independent tests.

## F. BT 与统计预检

- Common-matrix BT structural identifiability: 5 / 5 capability dimensions
- Numerical convergence: 5 / 5
- 500-run bootstrap convergence: 100% in each capability
- Separation warnings remain in C2, C3, and C5 and must be retained in later
  uncertainty reporting.
- Missing-aware Spearman outputs rho, p-value, pairwise n, and overlap matrices;
  pairs with n < 6 are explicitly labeled exploratory.

## G. 最终状态

`MODELING_READY_PENDING_HUMAN_SIGNOFF`

Automated gates pass. `FULLY_MODELING_READY` is prohibited until the 164-row
human verification checklist is completed and returned.
