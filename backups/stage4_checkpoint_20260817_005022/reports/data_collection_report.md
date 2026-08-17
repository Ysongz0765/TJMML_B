# Phase 3 Data Collection and Modeling-Readiness Report

## 1. 数据来源方法

Phase3 stopped broad benchmark expansion and searched only for evidence that
repairs C2/C3/C5 networks, adds independent Benchmark Families, cross-checks Kimi
K3, or reduces single-suite dependence. Structured official/archived payloads
were preferred. Search snippets and unverified summaries were never used as
numeric records.

New evidence sources include archived Artificial Analysis AA-LCR, HLE,
AA-Omniscience and MMMU-Pro pages; the DeepSeek V4 comparison table; and
supplementary official Google, Anthropic, OpenAI and Z.ai protocol documents.
Sources that could not be lawfully archived retain URL, title, access date and
an explicit `UNAVAILABLE` archive note.

## 2. 模型池

The formal core pool remains ten exact versions: Kimi K3 max reasoning, GPT-5.6
Sol max, GPT-5.5 xhigh, Claude Fable 5 max with fallback, Claude Opus 4.8 max,
Gemini 3.1 Pro High, DeepSeek V4 Pro Max, DeepSeek V4 Flash Max, Qwen3.8-Max,
and GLM-5.2 max. Kimi K3 remains mandatory. Qwen3-235B-A22B is historical
bridge evidence rather than the current Qwen core row.

## 3. Benchmark Family结构

The final hierarchy is Exact Setting -> Benchmark Family -> Capability ->
Overall Performance. The 21 settings form 14 families:

- C1: GPQA Diamond; LiveBench Math; LiveBench Logic
- C2: Humanity's Last Exam; AA-Omniscience
- C3: AA-LCR; MRCR; CorpusQA
- C4: LiveBench Coding; ProgramBench; FrontierSWE; SWE-bench Verified
- C5: MMMU-Pro; MathVision

LiveBench's ten task columns remain exact settings but receive only three
family-level concepts. Settings divide the family weight, preventing implicit
tenfold weighting.

## 4. 数据清洗与选择

All historical RawData rows were preserved. Phase3 added 33 rows and new fields
for family hierarchy and final selection. Raw values retain their source units:
fractions are not silently converted to percentages. Different HLE snapshots,
MMMU protocols, context lengths, tools, metrics and model endpoints remain
separate exact settings. Missing values remain `NA`.

## 5. 可比性与冲突

Only Grade A/B records with an exact model-setting identity can enter
FinalModelingMatrix. There are no strict source-conflict groups under the full
model + benchmark version + metric + tools + prompting + protocol key. Historical
vendor rows that differ from current third-party snapshots remain in RawData and
are not collapsed into one value.

## 6. 覆盖率与网络

FinalModelingMatrix has 164 / 210 observed cells (78.10%). Every core model has
at least 66.67% setting coverage and Kimi K3 has 85.71%. Eligible-model networks
are connected in all five capabilities. C3 nevertheless depends heavily on
AA-LCR: removing SRC014 reduces its largest-component ratio below the 80% gate.
C5 is modeled only among multimodal-applicable models.

## 7. 来源集中度

LiveBench supplies 60.98% of observed cells and dominates C1/C4 at the setting
level. This is acceptable only with family-level weighting and mandatory
LiveBench-exclusion sensitivity analysis. HLE, AA-LCR and MMMU-Pro bridges are
also tested with leave-one-source-out diagnostics.

## 8. 统计与BT预分析

Missing-aware Spearman matrices include pairwise sample sizes, overlap and
p-values. A family-deduplicated sensitivity analysis compares setting-equal and
family-equal weighting. Common and ExtendedEvidence BT smoke tests check graph
identifiability, convergence, condition numbers and separation; Common tests use
500 bootstrap iterations. No final model ranking is published at this stage.

## 9. 人工审核

No human override file was present. All selected records therefore remain
`human_verified=FALSE`. The final checklist contains exactly the 164 nonempty
matrix cells with score, record ID, source URL and page/table location.

## 10. 是否进入数学建模

Current status: `MODELING_READY_PENDING_HUMAN_SIGNOFF`.

- Missing-aware correlation analysis: suitable now for exploratory work.
- Latent capability estimation: suitable with family weights and missingness.
- Bradley-Terry/partial ranking: structurally suitable; retain separation and
  C3 source-dependence warnings.
- Bootstrap robust ranking: suitable after human sign-off, resampling families.
- Scenario evaluation: suitable and recommended, especially for multimodal
  applicability differences.

The binding decision and gate evidence are in
`reports/modeling_readiness_report.md` and
`data/processed/modeling_readiness_gate.xlsx`.
