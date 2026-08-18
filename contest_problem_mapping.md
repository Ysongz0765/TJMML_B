# Contest Problem Mapping

## Evidence note

The supplied `TJMML_B.pdf` was reopened and rendered page by page. Its Chinese
text layer is not recoverable: the PDF references missing Adobe-GB1 mappings
and the rendered pages preserve only fragments such as `B`, `Kimi K3`,
`DeepSeek`, `GPT`, `Claude`, and `AI`. The file therefore cannot be used to
quote the Chinese wording of the three questions without inventing text.

The mapping below uses the recoverable task structure encoded consistently in
the frozen data, the Q1--Q3 interfaces, and the existing formal outputs. It is
an audit of what the paper actually answers; it is not a claim that damaged
PDF glyphs have been reconstructed.

## Question-by-question audit

| 原题要求 | 当前论文对应章节 | 当前模型 | 当前是否真正回答 | 需要修改 |
| --- | --- | --- | --- | --- |
| 对题设给出的主流 AI 大模型进行综合性能评价，并说明不同公开评测结果如何进入比较 | 第 4 节 Q1：缺失感知的五维能力评价 | 缺失感知 Spearman、Family 平衡成对比较、正则化 Bradley--Terry、信息量--非冗余度--稳定性赋权、Bootstrap/LOFO | 部分回答。数学模型和正式结果完整，但旧正文偏向数据审计和接口说明，未充分用“题目要求--数学转译--结果含义”组织 | 重写问题重述、问题分析和 Q1 结果解释；正文减少 `frozen`、`bootstrap_id`、`interface` 等工程术语；覆盖图增加 C1--C5 分组 |
| 题目要求在不完整公开信息下比较模型能力，不能把未公开或不适用的结果直接解释为低分 | 第 4.1--4.4 节及附录数据说明 | `NA` 保持缺失；C5 结构性缺位单独标记；Common-N 与缺失感知相关性；Family-balanced BT | 已回答，但图 2 只区分 observed/NA，结构语义表达不足 | 在图 2 中区分 observed、ordinary missing、structural NA（仅在适用性审计有依据的 C5 单元显示）；正文说明完整案例删除和零填补的代价 |
| 由综合能力结果进一步回答不同任务场景下应选择哪些模型 | 第 5 节 Q2：考虑能力互补的场景效用 | KL 最小信息投影场景权重 + CES 聚合，场景内比较 Research/General/Coding 效用 | 基本回答。场景结果和权重来自正式 Q2 接口，但旧正文对科研、日常、代码的题意联系解释不足 | 以“上一问的综合排名为何不足以回答任务选择”为 Q2 开头；重做效用图为场景效用排名矩阵，说明颜色只表示场景内相对位置 |
| 解释不同场景中模型相对位置的变化，并检验能力互补参数变化对结论的影响 | 第 5.3--5.4 节 | 场景排名迁移、CES \(\rho\) 敏感性 | 部分回答。旧图为多条点线和效用折线，解释易退化为报数 | 改为 Bump Chart 和 CES 排名稳定性热图；正文明确“排名迁移来自场景需求映射，参数敏感性回答的是另一类稳健性问题” |
| 在性能满足场景需求的前提下考虑 API 价格、输入/输出 Token 负载和预算，给出部署选择 | 第 6 节 Q3：成本约束下的 Pareto 决策 | 工作负载成本、严格 FULL 成本队列、Pareto 前沿、预算切换点 | 已回答。成本、Pareto 和预算阈值与 frozen Q3 结果一致 | 将 Q3 开头改为“场景效用不能表达部署成本”；成本图强调输入/输出 Token 负载；预算图改为决策区间带并用正文给出分界线策略 |
| 不对缺失价格人工补值，并说明成本信息不完整对最终推荐的影响 | 第 6.2 节及附录价格快照 | FULL/PARTIAL/MISSING 可观测性分层；无人工补价 | 已回答，但旧正文夹杂 `FULL cohort`、`pricing audit` 等工程术语 | 正文改为“成本信息完整模型集合”“成本可核验性”；将追溯字段保留到附录 |

## Recursive relation among questions

The formal outputs support the following递进关系:

1. **Q1** identifies the capability profile of each candidate model from
   incomplete public evaluation records.
2. **Q2** maps that profile to the capability combination required by a
   specified task scene. A Q1 overall ranking alone cannot perform this
   mapping.
3. **Q3** adds workload cost and budget feasibility. A Q2 utility ranking
   alone cannot determine whether the model is affordable or cost-observable.

The manuscript should therefore close with:

\[
\text{基础能力识别}
\longrightarrow
\text{场景适配}
\longrightarrow
\text{预算约束下的决策}.
\]

## Terms retained from the formal model

The paper keeps the mathematical meanings of Benchmark Family, Exact Setting,
five dimensions \(C_1\)--\(C_5\), CES substitution parameter \(\rho\), utility
\(U_i^{(s)}\), cost \(C_i^{(s)}\), Pareto frontier, and frozen formal outputs.
The last term is used in the appendix and source notes, not as the narrative
subject of the main text.
