# Data Quality Report

## A. 数据规模
- RawData records after Phase2: 209
- Common Matrix models: 10
- Common Matrix benchmark settings: 19
- Phase1 overall coverage: 36.15%
- Phase2 Common Matrix coverage: 74.21%

## B. 来源质量
- Raw source authority counts: {'B': 101, 'A': 100, 'C': 8}
- Evidence role counts: {'COMMON_EVAL': 108, 'VENDOR_REPORT': 101}

## C. 缺失情况
- Overall Common Matrix missing rate: 25.79%
- Min model coverage: 52.63%
- Median model coverage: 76.32%
- Min benchmark coverage: 20.00%
- Median benchmark coverage: 100.00%

## D. 可比性
- Grade counts: {'Grade A': 100, 'Grade B': 91, 'Grade C': 18}
- Common Matrix Grade A/B ratio: 100.00%

## E. 冲突与交叉验证
- Automatic conflicts: 0
- CrossValidationRate: 0.0000

## F. 风险
- C3 long-context Common evidence remains sparse; MRCR/CorpusQA mainly connect DeepSeek variants.
- Qwen representative changed: Qwen3.8-Max is better for Common Matrix coverage, while Qwen3-235B-A22B remains bridge/extended evidence.
- OpenRouter GPQA model-version names do not perfectly match all first-stage model names, so GPT-5.6 Sol Pro was not mapped to GPT-5.6 Sol max.
- LiveBench task-level scores are unified and high-coverage, but they should not be collapsed with LiveBench composite indices.
- All machine-extracted/new records keep human_verified=FALSE pending manual audit.
