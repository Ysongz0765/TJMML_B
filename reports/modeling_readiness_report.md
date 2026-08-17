# LLM Benchmark Modeling Readiness Report - Frozen v1.0

来源访问日期：`2026-08-16`；正式冻结日期：`2026-08-17`

最终状态：`FULLY_MODELING_READY`

## 1. 最终CORE_MODEL

共10个精确模型版本：

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

Kimi K3按题目要求保留为核心对象。Qwen3-235B-A22B仅保留为历史Bridge/Extended证据，不进入正式核心矩阵。

## 2. Final Modeling Matrix

- 行数：10个CORE_MODEL
- Exact Benchmark Setting：21个
- Benchmark Family：14个
- 非空单元格：164 / 210
- 总覆盖率：78.10%
- 缺失率：21.90%
- 最低单模型覆盖率：66.67%（Qwen3.8-Max）
- Kimi K3覆盖率：85.71%

矩阵中的每个非空值均保留来源原始单位，并具有唯一`record_id`、`source_id`、URL及页码/表格位置。缺失值为`NA`，没有插值、预测或AI估算。

## 3. C1-C5准入结果

| Capability | 独立Family数 | Setting数 | 全部核心模型单元格覆盖 | Connected Components | LCC Ratio | BT状态 |
|---|---:|---:|---:|---:|---:|---|
| C1 Complex reasoning | 3 | 6 | 96.67% | 1 | 100% | 可识别并收敛 |
| C2 Knowledge/factual reliability | 2 | 2 | 80.00% | 1 | 100% | 可识别并收敛；有separation警告 |
| C3 Long context | 3 | 3 | 53.33% | 1 | 100% | 可识别并收敛；`FRAGILE_CONNECTED` |
| C4 Code/software engineering | 4 | 8 | 80.00% | 1 | 100% | 可识别并收敛 |
| C5 Multimodal | 2 | 2 | 50.00% | 4（全部10模型） | 70%（全部10模型） | 7个多模态适用模型中可识别并收敛 |

C5在7个多模态适用核心模型中的覆盖率为71.43%，Connected Components=1，LCC Ratio=100%。DeepSeek V4 Pro/Flash和GLM-5.2没有被填入虚构的多模态成绩，后续C5 BT只能在适用模型子集上解释。

## 4. LiveBench依赖

- Final Modeling Matrix中，LiveBench提供100 / 164个非空单元格，占60.98%。
- C1中占86.21%；C4中占78.13%；C2/C3/C5中为0。
- Overall source HHI约0.40；C1约0.76；C4约0.65，存在明显来源集中。

LiveBench的10个task不能视为10份独立顶层证据。正式权重规则为：Capability等权，Capability内Benchmark Family等权，同一Family中的settings再平分Family权重。

## 5. 删除LiveBench后的可识别性

- C2、C3、C5完全不受影响，因为最终数据不使用LiveBench填充这些维度。
- C1仅剩GPQA Diamond：8个有数据模型仍形成单一连通分量，局部BT可识别，但独立Family数由3降至1，不再满足完整能力准入要求。
- C4剩余14个单元格、3个Family、8个有数据模型；Connected Components=2，LCC Ratio=75%，BT不可识别。
- 因而，完整C1/C4结论存在LiveBench依赖；必须报告“含LiveBench”和“删除LiveBench”两套敏感性结果。

## 6. Benchmark去重/聚合

没有删除任何RawData历史证据。Final Modeling Matrix执行了以下选择：

- LiveBench数学3个task聚合到`LiveBench Math` Family；逻辑2个task聚合到`LiveBench Logic`；代码5个task聚合到`LiveBench Coding`。
- Phase2的厂商汇总`HLE-Full`不再作为最终默认setting，改用独立平台统一协议的`HLE Text-Only`快照；两者仍分别保留在RawData。
- 厂商汇总MMMU-Pro不与Artificial Analysis MMMU-Pro协议混列；最终矩阵只选后者作为统一桥接setting。
- Composite Index及其组成项不同时进入顶层评价。
- SWE-bench和SWE-bench Verified继续视为不同Benchmark；最终仅保留SWE-bench Verified setting。
- 相同题集的不同网页重复、Accuracy/EM派生metric和不同context length均未重复计权。

## 7. C2/C3/C5网络修复与Bridge Evidence

Phase3新增33条RawData记录。主要Bridge Evidence如下：

| Bridge | 新增记录 | 修复效果 | 来源等级 |
|---|---:|---|---|
| AA HLE text-only | 10 | C2 components 6 -> 1，LCC 50% -> 100% | C（独立第三方HLE评测） |
| AA-Omniscience | 6 | 为C2增加第二个独立Family；单独使LCC达到80% | A（Benchmark官方） |
| AA-LCR | 10 | C3 components 9 -> 1，LCC 20% -> 100% | A（Benchmark官方） |
| AA MMMU-Pro | 5 | C5适用模型components 3 -> 1，LCC 71.43% -> 100% | C（独立第三方MMMU评测） |
| DeepSeek Table 23 Gemini MRCR/CorpusQA | 2 | 将Gemini接入DeepSeek长上下文子网络 | B（厂商技术报告） |

C3的完全连通主要由AA-LCR提供。删除`SRC014`后C3的LCC Ratio降至30%，因此它不是稳健多桥网络，必须标记为`FRAGILE_CONNECTED`。

## 8. Kimi K3证据

| Capability | Kimi Setting覆盖 | Family数 | 来源数 | 网络Degree | 风险 |
|---|---:|---:|---:|---:|---|
| C1 | 6 / 6 = 100% | 3 | 2 | 9 | LiveBench占5/6，来源集中中等 |
| C2 | 2 / 2 = 100% | 2 | 2 | 9 | 两个Family均进入核心网络 |
| C3 | 1 / 3 = 33.33% | 1 | 1 | 9 | 高风险，仅AA-LCR单源/单Family |
| C4 | 7 / 8 = 87.50% | 3 | 2 | 9 | LiveBench占比高 |
| C5 | 2 / 2 = 100% | 2 | 2 | 6 | 在7个适用模型网络中完全连通 |

Kimi K3进入五个能力维度的主要网络，但C3证据仍明显不足；C3结果不得被描述为多Benchmark稳健验证。

## 9. Cross Validation

- Final Modeling Matrix严格独立、同版本、同metric、同setting的CrossValidationRate：0 / 164 = 0%。
- 五组关键Bridge Evidence完成了第二来源搜索，但0 / 5获得了可计为“独立重测且协议完全一致”的双源验证。
- Kimi K3最终建模记录中可计数的独立双源验证：0。

这是软目标未达成的主要剩余风险。厂商转载第三方成绩、相同来源镜像和不同快照/协议的相近数字均没有被冒充为独立验证。

## 10. 人工核验

- 核心记录：164条，即Final Modeling Matrix全部非空记录。
- 已人工核验：164条；未核验：0条。
- `human_verified=TRUE`仅写入这164条血缘锁定记录。
- 核验方法登记为`MANUAL_REVIEW_BY_TEAM`，记录日期为Stage 4写回日期`2026-08-17`。

参赛队员已在Stage 4前完成逐条人工来源核验；Stage 4仅写回该状态并运行自动一致性检查，不声称Codex执行了人工核验。

## 11. BT Smoke Test

Common数据在C1-C5的结构可识别性和数值收敛均通过；每个维度完成500次Bootstrap，结构可识别率和收敛率均为100%。

- C1：收敛，无separation警告。
- C2：收敛，有separation/高条件数警告。
- C3：收敛，有separation警告，且来源删除敏感。
- C4：收敛，无separation警告；删除LiveBench后不再可识别。
- C5：在7个多模态适用模型中收敛，有separation警告。

这些仅为建模准入和数值稳定性测试，不是最终模型排名。

## 12. 最终状态

`FULLY_MODELING_READY`

原因：G1-G9及BT自动准入检查通过；10个核心模型、14个Benchmark Families、网络结构、缺失感知统计、164/164人工核验写回和164/164追溯链均已完成。LiveBench集中、C3单源桥、C5适用范围和C2/C3/C5 separation警告均已显式保留，不阻断正式建模，但必须进入论文限制与敏感性分析。

## 后续数学建模建议

- Benchmark相关性分析：可以；只解释pairwise n>=6的结果。
- 潜在能力估计：可以；按Family等权并显式处理缺失。
- Bradley-Terry/部分排序：可以开展预分析；C3必须做去SRC014敏感性，C5限适用模型。
- Bootstrap稳健排名：可以正式开展；重采样单位应为Benchmark Family。
- 场景化评价：可以，且适合处理多模态不适用模型。

## 图件与QC

- 已生成21组PNG+SVG图件，目录：`reports/figures/stage3/`。
- 指定图型包括缺失热力图、Family层级、来源占比与HHI、C1-C5网络、C2/C3/C5修复前后、LCC比例、Family覆盖、Spearman、pairwise n、LiveBench删除对比及数据流程图。
- 总Excel含31个Sheet；全Sheet渲染通过；公式错误扫描为0。
- 最终自动QC：`reports/stage3_final_qc_summary.json`，状态`PASS`。
