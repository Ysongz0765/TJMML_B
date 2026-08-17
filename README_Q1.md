# 问题一可复现建模说明

## 数据输入

本流程只读取 `frozen/v1.0/`。运行前会核验 `SHA256SUMS_v1.0.txt`，并复核 10 个核心模型、14 个 Benchmark Families、21 个 Exact Settings、164 条非缺失核心记录、人工核验 164/164、冻结日期 2026-08-17。

## 数学方法

主线为 missing-aware Spearman 相关性分析、Benchmark Family 冗余诊断、Family-balanced margin-weighted regularized Bradley-Terry、C1-C5 潜在能力估计、信息-冗余-稳定性客观赋权、missing-aware 综合评分、family-aware bootstrap 与敏感性分析。

缺失值保持为 `NaN/NA`。C5 缺失模型不填 0，综合分按模型实际可用维度对权重重新归一。

## 如何运行

```bash
python -m src.q1.run_q1
```

默认 bootstrap 次数为 2000。调试时可临时设置：

```bash
$env:Q1_BOOTSTRAP_B="500"
python -m src.q1.run_q1
```

## 输出文件

所有结果写入 `outputs/q1/`，包含：

- `tables/`: q1 全流程表格和论文表格。
- `figures/`: PNG、SVG、PDF 三种格式图件。
- `diagnostics/model_diagnostics.json`: BT 与网络诊断。
- `bootstrap/`: bootstrap 明细 CSV。
- `results_summary.json` 与 `results_summary.md`: 论文写作数字摘要。

## 参数

- `lambda`: 主模型为 1.0，敏感性比较 `[0.1, 0.3, 1, 3, 10]`。
- margin 权重: 主模型为 range-normalized，敏感性比较 no-margin 与 robust IQR。
- random seed: 20260817。
- redundancy threshold: 0.80、0.85、0.90 均输出诊断，主表使用 0.85 标记候选。

## 已知数据限制

C3 对 AA-LCR 有结构依赖，C4 对 LiveBench Coding 有桥接依赖，C5 仅适用于有多模态 benchmark 的模型。上述限制只作为诊断和敏感性分析呈现，不改变 frozen/v1.0 的正式 family mapping。
