# Q1 → Q2 标准数据接口

## 1. 目的与边界

Q2 不导入 `src/q1/` 的代码，也不依赖 Q1 内部文件结构、Bradley–Terry 成对比较过程或任何临时输出。Q1 冻结后只需交付一份标准 CSV 和一份 metadata JSON；若 Q1 的维度名称或导出形式调整，只修改 `src/q2/data_adapter.py`。

Q2 的主输入是每个模型在统一能力空间中的最终能力向量。Q1 综合分、综合排名、Bootstrap 区间等均为可选信息，不是 KL-CES 主模型运行的必要条件。

## 2. 必须交付的 CSV 字段

| 字段 | 类型 | 范围/单位 | 含义 |
|---|---|---|---|
| `model` | string | 非空且唯一 | 模型显示名称；正式分析 Kimi 时需与目标名约定一致 |
| `C1` | number/NA | 由 metadata 声明为 0–100 或 0–1 | 复杂推理能力 |
| `C2` | number/NA | 同上 | 知识与事实可靠性 |
| `C3` | number/NA | 同上 | 长上下文处理能力 |
| `C4` | number/NA | 同上 | 代码与软件工程能力 |
| `C5` | number/NA | 同上 | 多模态能力 |
| `C1_available` … `C5_available` | boolean | `TRUE/FALSE` | 对应能力是否具有 Q1 认可的可用结果 |

一致性规则：能力标记为 `TRUE` 时必须有数值；标记为 `FALSE` 时 Q2 会把该能力视为 NA，即使 CSV 中误留数值也不会当作观测值使用。Q2 不把 NA 填成 0。

## 3. Q1 客观权重

Q1 应在 metadata 的 `objective_weights` 对象中提供 `C1`–`C5` 五个严格为正的权重，并设置：

```json
"objective_weights_available": true
```

权重可不严格加总为 1，适配层会归一化。其解释口径为：五类能力在当前公开评测数据中的信息贡献、非冗余性与稳定性形成的中性参考分布，而不是具体使用场景中的直接价值权重。

## 4. 必须交付的冻结 metadata

| 字段 | FINAL 要求 | 说明 |
|---|---|---|
| `q1_finalized` | 必须为 `true` | Q1 已经由负责人确认冻结 |
| `q1_freeze_version` | 必须非空 | 如 `q1-v1.0` |
| `q1_freeze_date` | 必须非空 | 建议 ISO 日期或时间戳 |
| `ability_scale` | 必须为 `0-100` 或 `0-1` | Q2 据此统一到 0–1 |
| `objective_weights_available` | 必须为 `true` | 正式 Q1 先验可用 |
| `objective_weights` | 必须含 C1–C5 | KL 投影的基础参考分布 |
| `q1_missing_policy_applied` | 视情况 | 若 Q1 已统一处理缺失并要求 Q2 继承，则设为 `true` |
| `q1_missing_policy_name` | 建议 | 记录 Q1 最终缺失策略名称/版本 |

只要 `q1_finalized`、冻结版本、冻结日期或客观权重任一条件缺失，`MODE=FINAL` 就会被程序拒绝。

## 5. 可选 CSV 字段

| 字段 | 类型 | 用途 |
|---|---|---|
| `q1_overall_score` | number | 描述性对照，不进入 Q2 主效用 |
| `q1_overall_rank` | positive integer | 构造 Q1 baseline → 三场景的排名迁移；缺失时只比较三个场景 |
| `C1_lower`, `C1_upper` … `C5_lower`, `C5_upper` | number/NA | 区间传播与最好/最差可能排名 |

区间字段可以来自 Bootstrap 置信区间、Q1 缺失能力界或其他经 Q1 冻结认可的上下界。必须满足 `0 ≤ lower ≤ upper ≤ scale maximum`。若某能力点值已观测、区间字段缺失，区间传播将把点值视为退化区间；若能力点值缺失，则上下界必须同时提供。

## 6. 模板与交付文件

- 最小结构：`data/q2/q1_input_template.csv`
- 正式扩展结构：`data/q2/q1_final_input_template.csv`
- metadata：`data/q2/q1_final_metadata_template.json`

正式交付时应复制模板另存为明确带冻结版本的文件，不应直接把模板本身改成结果文件。

## 7. Q2 缺失策略选择

Q2 支持：

1. `complete_case`：仅保留五维均可观测模型；
2. `common_dimension`：仅采用所有参与模型共同可观测维度，并在该维度集合上重新归一化先验、重新求解场景权重，结果标记 `COMMON_DIMENSION_RESULT`；
3. `interval_propagation`：使用 Q1 提供的上下界传播 CES 效用区间及可能排名；
4. `q1_final_policy`：Q1 已冻结统一处理策略时直接继承，但 metadata 必须明确声明。

策略选择属于正式建模决策。Q2 不自行生成不存在的能力值。

## 8. Q1 负责人最小交接清单

- [ ] 一行对应一个模型，模型名唯一；
- [ ] C1–C5 与 availability flags 完整；
- [ ] 能力量纲和范围明确；
- [ ] Q1 客观权重完整且严格为正；
- [ ] `q1_finalized=true`；
- [ ] 冻结版本和日期非空；
- [ ] 若提供综合排名，说明并列名次口径；
- [ ] 若提供区间，说明区间来源与置信水平；
- [ ] 若要求继承 Q1 缺失策略，metadata 中明确标记。
