# 数据来源与数据处理

## 1. 数据来源

本文以具体模型版本为评价对象，优先采用Benchmark官方排行榜或官方结果、采用统一协议重新评测多个模型的独立平台，以及模型厂商发布的官方技术报告、模型卡和论文。Arena等真实场景数据不进入Q1基础Benchmark矩阵，仅用于后续场景化外部验证。

本文优先选择同一评价协议下同时覆盖多个目标模型的数据。当统一评测结果缺失时，使用Benchmark官方资料或模型官方技术报告补充。每条记录均保存模型精确版本、Benchmark及版本、Exact Setting、metric、工具条件、推理配置、来源与访问日期；协议不可比的数据不进入核心矩阵。

## 2. 数据规模

冻结版本`v1.0`包含10个核心模型、14个Benchmark Families和21个Exact Settings，共164个有效核心观测，总覆盖率为78.10%。Kimi K3覆盖率为85.71%，最低单模型覆盖率为66.67%。核心模型为：Kimi K3 (max reasoning)、GPT-5.6 Sol (max)、GPT-5.5 (xhigh)、Claude Fable 5 (max, with fallback)、Claude Opus 4.8 (max)、Gemini-3.1-Pro (High)、DeepSeek-V4-Pro Max、DeepSeek-V4-Flash Max、Qwen3.8-Max、GLM-5.2 (max)。

## 3. 缺失值处理

不同模型的公开评测覆盖具有结构性缺失。本文不采用均值、KNN、回归预测或AI估计等方式生成Benchmark成绩，无法获得可靠可比来源的单元格统一保留为NA，后续使用能够处理不完全比较关系的方法建模。

## 4. Benchmark Family机制

为避免任务数量较多的Benchmark Suite获得隐性重复权重，本文建立“Exact Setting → Benchmark Family → Capability Dimension → Overall Performance”层级。同一Family内部settings先进行均衡处理，再进入能力层评价。

## 5. 可比性与人工核验

核心记录必须满足Benchmark版本、metric、tools/no-tools、reasoning setting及评测协议可比。最终进入建模矩阵的全部164条记录均由参赛队员人工对照公开原始来源核验，核验范围包括模型版本、Benchmark及版本、metric、score、工具/推理条件与原始来源。Codex仅负责将已完成的人工核验状态写回数据系统并运行自动QC。
