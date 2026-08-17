# LLM Benchmark Dataset v1.0

## 数据冻结日期

`2026-08-17`

## 数据版本

`v1.0`。v1.0不得原位修改；后续纠错必须发布v1.1并保留本目录。

## 核心模型

1. Kimi K3 (max reasoning)
2. GPT-5.6 Sol (max)
3. GPT-5.5 (xhigh)
4. Claude Fable 5 (max, with fallback)
5. Claude Opus 4.8 (max)
6. Gemini-3.1-Pro (High)
7. DeepSeek-V4-Pro Max
8. DeepSeek-V4-Flash Max
9. Qwen3.8-Max
10. GLM-5.2 (max)

## 数据规模

- 10个模型
- 21个Exact Settings
- 14个Benchmark Families
- 164个有效核心观测
- 78.10%总体覆盖率
- Kimi K3覆盖率85.71%
- 最低模型覆盖率66.67%

## 数据来源原则

优先使用Benchmark官方结果和统一协议评测；缺失时使用模型官方技术报告或模型卡补充。External Validation数据不自动进入Q1核心矩阵。

## 数据缺失原则

缺失值保持NA，不进行人工插值、预测或AI估算。

## Benchmark Family原则

采用`Exact Setting → Benchmark Family → Capability`层级，Family内部settings先均衡处理。

## 人工核验

最终正式建模数据已由参赛队员人工对照公开原始来源核验。Codex仅负责将人工核验状态写回数据系统并运行自动QC。
