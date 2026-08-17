# 附录D 数据预处理与可比性规则

1. **Benchmark版本一致性**：不同年份、版本和数据子集均视为不同Exact Settings。
2. **Metric一致性**：Accuracy、EM、pass@1、pass@k等不得直接合并。
3. **Tools条件**：tools与no-tools分别记录，禁止直接横向混合。
4. **Reasoning setting**：low、medium、high、xhigh、max等配置分别保存。
5. **Harness规则**：不同Agent harness默认不可直接等同；仅在协议说明充分时进入同一比较。
6. **Benchmark Family去重**：同Suite的相关子任务先在Family内部均衡，避免重复计权。
7. **缺失值规则**：可靠数据缺失时保留NA，不插值、不预测、不进行AI估算。
8. **Composite Index**：综合指数与其组成Benchmark不同时作为独立顶层指标。
9. **人工核验**：正式矩阵的全部非空记录由参赛队员核对模型、setting、metric、score和来源；系统只记录核验结果。
10. **数据冻结**：正式Q1默认使用v1.0；后续纠错必须发布v1.1并保留v1.0。
