# 附录：数学建模支撑材料与核心源程序

## 一、附录范围

本附录包括直接参与 Q1--Q3 问题求解的数学模型、冻结输入、模型参数、数值结果、稳健性检验和完整数学计算模块。

保留范围如下：

- Q1：缺失感知 Spearman、Benchmark Family 平衡、正则化 Bradley--Terry、五维能力、客观权重、Bootstrap、LOFO、LOSO 与等权敏感性；
- Q2：能力正值变换、KL 最小信息投影、CES 效用、线性基准、短板惩罚、边际效用、不确定性传播和参数敏感性；
- Q3：标准工作负载成本、成本可观测性队列、Pareto 前沿、预算选择、增量成本效果、成本--性能拟合和敏感性分析。

本附录没有为缺失 Benchmark 补零或插值，没有为 Claude Fable 5 的 fallback 配置或 GLM-5.2 补造价格。两者仍分别按 `PARTIAL` 和 `MISSING` 保留，不进入严格 FULL 成本主队列。

## 二、建模版本基准

| 建模部分 | 仓库分支 | 提交 | 正式入口/规范 |
|---|---|---|---|
| Q1 v1.2 | `q2-final-paper` | `bff0e185510f79bd78dd190ccedc47c81b12f137` | `src/q1/run_q1_v12.py` |
| Q2 KL-CES | `q2-final-paper` | `bff0e185510f79bd78dd190ccedc47c81b12f137` | `q2/model_spec_v1.yaml`、`src/q2/pipeline.py` |
| Q3 Cost-Pareto | `q3-cost-pareto` | `637a55e763f299080b78522e22fe867d31551e01` | `q3/src/` 数值计算模块 |

## 三、支撑材料压缩包文件列表

支撑材料压缩文件为 `final_paper_v3_支撑材料.zip`，压缩包大小为 6,990,740 字节（6.67 MiB），SHA-256 为 `dff4ee2aa4e2669f7d0e15eb0b7456d23583afeab662f6ad721922b85057abeb`。压缩包内共有 247 个文件，其中 `支撑材料文件清单.csv` 为总清单；下表列出清单记录的 246 项支撑材料，未压缩总大小为 38.95 MiB。逐文件完整 SHA-256 保存在包内 `支撑材料文件清单.csv`，清单 CSV 自身不参与自引用哈希。

| 类别 | 文件数 | 大小（MiB） |
|---|---:|---:|
| Q1 中间结果图表 | 8 | 0.86 |
| Q1 冻结输入 | 17 | 2.42 |
| Q1 建模程序 | 10 | 0.05 |
| Q1 数值结果与稳健性输出 | 24 | 0.15 |
| Q2 中间结果图表 | 6 | 1.09 |
| Q2 建模程序与规范 | 16 | 0.05 |
| Q2 建模输入 | 13 | 0.06 |
| Q2 数值结果与接口输出 | 57 | 11.50 |
| Q3 中间结果图表 | 21 | 2.10 |
| Q3 建模程序 | 9 | 0.03 |
| Q3 建模说明与审计 | 5 | 0.01 |
| Q3 建模输入与冻结数据 | 31 | 20.50 |
| Q3 数值结果与模型诊断 | 26 | 0.10 |
| 复现环境 | 1 | 0.00 |
| 完整性校验 | 1 | 0.02 |
| 支撑材料说明 | 1 | 0.00 |

<details>
<summary>展开仅建模逐文件清单</summary>

| 序号 | 相对路径 | 类别 | 建模用途 | 字节数 | SHA-256 |
|---:|---|---|---|---:|---|
| 1 | `README_支撑材料说明.md` | 支撑材料说明 | 目录结构、运行环境与数据口径说明 | 1898 | `86c910105fc9406f…` |
| 2 | `SHA256SUMS.txt` | 完整性校验 | 支撑材料逐文件 SHA-256 汇总 | 26196 | `381d5737f8f1f588…` |
| 3 | `figures/q1/figure_q1_v12_01_flow.png` | Q1 中间结果图表 | Q1 建模流程 | 90037 | `85ed298ea60a03bf…` |
| 4 | `figures/q1/figure_q1_v12_02_coverage.png` | Q1 中间结果图表 | Q1 数据覆盖率 | 105666 | `2e70164af47f0961…` |
| 5 | `figures/q1/figure_q1_v12_03_spearman.png` | Q1 中间结果图表 | Q1 缺失感知相关性 | 175772 | `7a8752e63c895d78…` |
| 6 | `figures/q1/figure_q1_v12_04_dimension_scores.png` | Q1 中间结果图表 | Q1 五维能力得分 | 95476 | `54cbad8a965d9230…` |
| 7 | `figures/q1/figure_q1_v12_05_ranking_A_ci.png` | Q1 中间结果图表 | Q1 综合排序与置信区间 | 98024 | `41f7ec052aea9fc6…` |
| 8 | `figures/q1/figure_q1_v12_06_lofo_rank_change.png` | Q1 中间结果图表 | Q1 LOFO 稳健性 | 179029 | `e6787de81c4960cc…` |
| 9 | `figures/q1/figure_q1_v12_07_kimi_gap.png` | Q1 中间结果图表 | Q1 Kimi 优势差距 | 35090 | `ce48835c6b4d9fd3…` |
| 10 | `figures/q1/figure_q1_v12_loso_rank_change.png` | Q1 中间结果图表 | Q1 LOSO 稳健性 | 119744 | `8d3c7843e487519c…` |
| 11 | `figures/q2/q2_fig1_framework.png` | Q2 中间结果图表 | Q2 模型框架 | 99626 | `4f4d5610b6725c05…` |
| 12 | `figures/q2/q2_fig2_scene_weights.png` | Q2 中间结果图表 | Q2 场景权重 | 87772 | `5febbf3d058a2248…` |
| 13 | `figures/q2/q2_fig3_utility_heatmap.png` | Q2 中间结果图表 | Q2 场景效用 | 250468 | `c44ded698fbe4462…` |
| 14 | `figures/q2/q2_fig4_rank_migration.png` | Q2 中间结果图表 | Q2 排名迁移 | 390967 | `b8e52dbc4bb21481…` |
| 15 | `figures/q2/q2_fig5_kimi_alpha_rho.png` | Q2 中间结果图表 | Q2 参数敏感性 | 203823 | `fb345b7ca3374a2c…` |
| 16 | `figures/q2/q2_fig6_kimi_mechanism.png` | Q2 中间结果图表 | Q2 效用机制 | 107844 | `dbfbef492b72da30…` |
| 17 | `figures/q3/q3_budget_steps_Coding.png` | Q3 中间结果图表 | Q3 预算切换阶梯 | 68944 | `da4f8d904ee316ed…` |
| 18 | `figures/q3/q3_budget_steps_General.png` | Q3 中间结果图表 | Q3 预算切换阶梯 | 60187 | `a40e93332a0287e7…` |
| 19 | `figures/q3/q3_budget_steps_Research.png` | Q3 中间结果图表 | Q3 预算切换阶梯 | 57938 | `6adef259826880d8…` |
| 20 | `figures/q3/q3_cost_performance_fit_Coding.png` | Q3 中间结果图表 | Q3 成本—性能拟合 | 110392 | `db3c3943b37cedb4…` |
| 21 | `figures/q3/q3_cost_performance_fit_General.png` | Q3 中间结果图表 | Q3 成本—性能拟合 | 101329 | `ef4c840d102b0ebe…` |
| 22 | `figures/q3/q3_cost_performance_fit_Research.png` | Q3 中间结果图表 | Q3 成本—性能拟合 | 128913 | `e9ee883cf8f4a451…` |
| 23 | `figures/q3/q3_cost_utility_Coding.png` | Q3 中间结果图表 | Q3 成本—效用关系 | 131852 | `b46b3e057e3a4e93…` |
| 24 | `figures/q3/q3_cost_utility_General.png` | Q3 中间结果图表 | Q3 成本—效用关系 | 126066 | `007cbabe5d09bb77…` |
| 25 | `figures/q3/q3_cost_utility_Research.png` | Q3 中间结果图表 | Q3 成本—效用关系 | 134807 | `afc950ba53fbb2f5…` |
| 26 | `figures/q3/q3_icer_Coding.png` | Q3 中间结果图表 | Q3 增量成本效果 | 84449 | `6852d4f3ddb75038…` |
| 27 | `figures/q3/q3_icer_General.png` | Q3 中间结果图表 | Q3 增量成本效果 | 134535 | `9a1ecd5b1f348509…` |
| 28 | `figures/q3/q3_icer_Research.png` | Q3 中间结果图表 | Q3 增量成本效果 | 85319 | `cf57f16d7f4b3f0d…` |
| 29 | `figures/q3/q3_pareto_probability_Coding.png` | Q3 中间结果图表 | Q3 Pareto 概率 | 113142 | `409011ac1abaff80…` |
| 30 | `figures/q3/q3_pareto_probability_General.png` | Q3 中间结果图表 | Q3 Pareto 概率 | 113105 | `ed6e02ddbdd2ab78…` |
| 31 | `figures/q3/q3_pareto_probability_Research.png` | Q3 中间结果图表 | Q3 Pareto 概率 | 113815 | `c097e66eb25d1f8e…` |
| 32 | `figures/q3/q3_price_perturbation_Coding.png` | Q3 中间结果图表 | Q3 价格扰动敏感性 | 119420 | `8d203b24d141f6cd…` |
| 33 | `figures/q3/q3_price_perturbation_General.png` | Q3 中间结果图表 | Q3 价格扰动敏感性 | 121896 | `9c681e94712e0e49…` |
| 34 | `figures/q3/q3_price_perturbation_Research.png` | Q3 中间结果图表 | Q3 价格扰动敏感性 | 117563 | `8ab182010d67f98a…` |
| 35 | `figures/q3/q3_ratio_sensitivity_Coding.png` | Q3 中间结果图表 | Q3 工作负载比例敏感性 | 95204 | `52c9bab88f1545cf…` |
| 36 | `figures/q3/q3_ratio_sensitivity_General.png` | Q3 中间结果图表 | Q3 工作负载比例敏感性 | 92335 | `f3795bca844a837d…` |
| 37 | `figures/q3/q3_ratio_sensitivity_Research.png` | Q3 中间结果图表 | Q3 工作负载比例敏感性 | 87327 | `6c24a5973389d358…` |
| 38 | `frozen/v1.0/README.md` | Q1 冻结输入 | 模型假设、数据口径或稳健性说明 | 1251 | `9c3bc4427ed25eb3…` |
| 39 | `frozen/v1.0/SHA256SUMS_v1.0.txt` | Q1 冻结输入 | Q1 冻结输入完整性校验 | 1556 | `12e94949be5a55d3…` |
| 40 | `frozen/v1.0/analysis_bundle_v1.0.json` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 2043897 | `015429605eebc811…` |
| 41 | `frozen/v1.0/benchmark_family_manifest_v1.0.csv` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 19678 | `17e9d7a1b93a86b5…` |
| 42 | `frozen/v1.0/benchmark_family_manifest_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 11155 | `78877a2cac971ec3…` |
| 43 | `frozen/v1.0/data_freeze_manifest_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 7204 | `cd82be2a91778eda…` |
| 44 | `frozen/v1.0/final_modeling_benchmark_manifest_v1.0.csv` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 6188 | `1a0d5c9697216b43…` |
| 45 | `frozen/v1.0/final_modeling_benchmark_manifest_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 7427 | `d8a722c4ca210776…` |
| 46 | `frozen/v1.0/final_modeling_matrix_v1.0.csv` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 3248 | `6172fb9a417665af…` |
| 47 | `frozen/v1.0/final_modeling_matrix_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 25521 | `08e5e5845aaa61e1…` |
| 48 | `frozen/v1.0/human_verification_log_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 24610 | `779f78fa3d54556f…` |
| 49 | `frozen/v1.0/model_pool_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 6062 | `5abf6fea6852e9ce…` |
| 50 | `frozen/v1.0/modeling_readiness_gate_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 8882 | `ebe375d2fee656a1…` |
| 51 | `frozen/v1.0/raw_benchmark_data_v1.0.csv` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 284448 | `3087da633064b5a9…` |
| 52 | `frozen/v1.0/raw_benchmark_data_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 72853 | `e647bfd3f98f89f7…` |
| 53 | `frozen/v1.0/source_registry_v1.0.csv` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 7745 | `8408edc25b87cde8…` |
| 54 | `frozen/v1.0/source_registry_v1.0.xlsx` | Q1 冻结输入 | 模型输入、数值输出或机器可读审计 | 8537 | `756d2229491ccd1e…` |
| 55 | `outputs/q1_v1.2/diagnostics/bootstrap_method.md` | Q1 数值结果与稳健性输出 | 模型假设、数据口径或稳健性说明 | 1456 | `5e98ccff42646e66…` |
| 56 | `outputs/q1_v1.2/diagnostics/quality_checks.json` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 790 | `a8d8ab28449ac0c8…` |
| 57 | `outputs/q1_v1.2/diagnostics/stability_audit.md` | Q1 数值结果与稳健性输出 | 模型假设、数据口径或稳健性说明 | 2729 | `cd5383a3b077488a…` |
| 58 | `outputs/q1_v1.2/results_summary_v1.2.json` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 25832 | `2bb97957db4b66ab…` |
| 59 | `outputs/q1_v1.2/results_summary_v1.2.md` | Q1 数值结果与稳健性输出 | 模型假设、数据口径或稳健性说明 | 2224 | `1195c584b3d9cd34…` |
| 60 | `outputs/q1_v1.2/sensitivity/lofo_model_changes_v1.2.csv` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 7568 | `2881cfea5b5a1ecc…` |
| 61 | `outputs/q1_v1.2/sensitivity/lofo_summary_v1.2.csv` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 2499 | `0483f9d564a63fa1…` |
| 62 | `outputs/q1_v1.2/sensitivity/loso_model_changes_v1.2.csv` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 1863 | `8ec8748d598bb899…` |
| 63 | `outputs/q1_v1.2/sensitivity/loso_summary_v1.2.csv` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 988 | `ff4f07b06efcaaf7…` |
| 64 | `outputs/q1_v1.2/tables/manual_capability_verification_v1.2.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 5371 | `6a71cbe181b47eaf…` |
| 65 | `outputs/q1_v1.2/tables/paper_table_q1_v12_bootstrap.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 9042 | `7095c4fabc8b1374…` |
| 66 | `outputs/q1_v1.2/tables/paper_table_q1_v12_dimension_scores.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 8360 | `6066bd1990b0a878…` |
| 67 | `outputs/q1_v1.2/tables/paper_table_q1_v12_dimension_weights.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 7159 | `d6ac86c8da2d8cf1…` |
| 68 | `outputs/q1_v1.2/tables/paper_table_q1_v12_indicator_screening.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 5377 | `a0f1654854c9f871…` |
| 69 | `outputs/q1_v1.2/tables/paper_table_q1_v12_ranking_A.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 6970 | `58c624bdcce58552…` |
| 70 | `outputs/q1_v1.2/tables/paper_table_q1_v12_ranking_B_C1_C4.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 6720 | `3024677ba7097dc5…` |
| 71 | `outputs/q1_v1.2/tables/paper_table_q1_v12_ranking_C_estimable_c5_multimodal.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 6605 | `9223efd422b7dc50…` |
| 72 | `outputs/q1_v1.2/tables/paper_table_q1_v12_screening.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 7945 | `eaf43c4bfb34742d…` |
| 73 | `outputs/q1_v1.2/tables/paper_table_q1_v12_sources.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 4921 | `5ef38234e7214cd6…` |
| 74 | `outputs/q1_v1.2/tables/table_q1_v12_c5_applicability_audit.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 5398 | `47c1ebde49d2398e…` |
| 75 | `outputs/q1_v1.2/tables/table_q1_v12_equal_weight_sensitivity.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 6804 | `49d691ca14ca7f60…` |
| 76 | `outputs/q1_v1.2/tables/table_q1_v12_lofo.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 13713 | `407deba362e1b469…` |
| 77 | `outputs/q1_v1.2/tables/table_q1_v12_loso.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 8515 | `a16723a6486eac89…` |
| 78 | `outputs/q1_v1.2/tables/table_q1_v12_robustness_summary.xlsx` | Q1 数值结果与稳健性输出 | 模型输入、数值输出或机器可读审计 | 8372 | `9883c5f1aa9ef7b0…` |
| 79 | `outputs/q2/final/Q2_FINAL_AUDIT_REPORT.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1909 | `b54eac7c71d60187…` |
| 80 | `outputs/q2/final/README.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 815 | `35dfa3e9d6c9d2e7…` |
| 81 | `outputs/q2/final/c5_policy_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 716 | `e1d0360804e3e75b…` |
| 82 | `outputs/q2/final/ces_input_transformation_audit.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 13403 | `19a93b7311968050…` |
| 83 | `outputs/q2/final/ces_input_transformation_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 735 | `6ad8b6b468ce2295…` |
| 84 | `outputs/q2/final/freeze/Q2_FINAL_AUDIT_REPORT.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1909 | `b54eac7c71d60187…` |
| 85 | `outputs/q2/final/freeze/c5_policy_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 716 | `e1d0360804e3e75b…` |
| 86 | `outputs/q2/final/freeze/ces_input_transformation_audit.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 13403 | `19a93b7311968050…` |
| 87 | `outputs/q2/final/freeze/ces_input_transformation_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1015 | `95ec533d22ff4030…` |
| 88 | `outputs/q2/final/freeze/model_spec_provenance_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1005 | `0202cb5252330334…` |
| 89 | `outputs/q2/final/freeze/pri_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 564 | `ef2637268460082a…` |
| 90 | `outputs/q2/final/freeze/q1_uncertainty_scale_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1483 | `fbc2c87cb701db9a…` |
| 91 | `outputs/q2/final/freeze/q2_freeze_manifest.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 4115 | `e2d36a500fa0bf43…` |
| 92 | `outputs/q2/final/freeze/q2_kimi_analysis.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 1715 | `073fb2f8bf111ded…` |
| 93 | `outputs/q2/final/freeze/q2_linear_vs_ces.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 2822 | `1daf32a10d379c97…` |
| 94 | `outputs/q2/final/freeze/q2_marginal_effects.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 9825 | `32e434d5dcc95412…` |
| 95 | `outputs/q2/final/freeze/q2_missingness_sensitivity.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 28017 | `13494de2b162bb7c…` |
| 96 | `outputs/q2/final/freeze/q2_model_spec_snapshot.yaml` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 4269 | `203f8f237d5f65f2…` |
| 97 | `outputs/q2/final/freeze/q2_parameter_robustness.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 8159 | `39ebf920c78a2112…` |
| 98 | `outputs/q2/final/freeze/q2_pri.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 3896 | `0f7fa9039674988d…` |
| 99 | `outputs/q2/final/freeze/q2_prior_sensitivity.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 7203 | `1de342269659758f…` |
| 100 | `outputs/q2/final/freeze/q2_q1_uncertainty_propagation.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 5176 | `cbc0b66bc15fa8fb…` |
| 101 | `outputs/q2/final/freeze/q2_rank_transition_thresholds.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 57525 | `1d7723b4c163c00c…` |
| 102 | `outputs/q2/final/freeze/q2_run_metadata.json` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 6907 | `d10839c302f26464…` |
| 103 | `outputs/q2/final/freeze/q2_scene_rankings.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 2081 | `18732ce0c9d3e63f…` |
| 104 | `outputs/q2/final/freeze/q2_scene_scores.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 10908 | `7540c845e487fb67…` |
| 105 | `outputs/q2/final/freeze/q2_scene_weights.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 3008 | `5eb3b6871639f7f4…` |
| 106 | `outputs/q2/final/freeze/rank_migration_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 485 | `1f2277f250f30c70…` |
| 107 | `outputs/q2/final/freeze/scene_definition_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 613 | `a480c08fb4928d87…` |
| 108 | `outputs/q2/final/model_spec_provenance_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1005 | `0202cb5252330334…` |
| 109 | `outputs/q2/final/pri_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 564 | `ef2637268460082a…` |
| 110 | `outputs/q2/final/q1_uncertainty_scale_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 1483 | `fbc2c87cb701db9a…` |
| 111 | `outputs/q2/final/q2_equal_prior_reference_scores.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 10969 | `0c74410b28963413…` |
| 112 | `outputs/q2/final/q2_freeze_manifest.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 4115 | `e2d36a500fa0bf43…` |
| 113 | `outputs/q2/final/q2_kimi_analysis.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 1715 | `073fb2f8bf111ded…` |
| 114 | `outputs/q2/final/q2_linear_vs_ces.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 2822 | `1daf32a10d379c97…` |
| 115 | `outputs/q2/final/q2_marginal_effects.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 9825 | `32e434d5dcc95412…` |
| 116 | `outputs/q2/final/q2_missingness_sensitivity.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 28017 | `13494de2b162bb7c…` |
| 117 | `outputs/q2/final/q2_model_spec_snapshot.yaml` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 4269 | `203f8f237d5f65f2…` |
| 118 | `outputs/q2/final/q2_parameter_grid.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 870331 | `de81762993c9084c…` |
| 119 | `outputs/q2/final/q2_parameter_robustness.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 8159 | `39ebf920c78a2112…` |
| 120 | `outputs/q2/final/q2_pri.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 3896 | `0f7fa9039674988d…` |
| 121 | `outputs/q2/final/q2_prior_sensitivity.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 7203 | `1de342269659758f…` |
| 122 | `outputs/q2/final/q2_q1_uncertainty_propagation.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 5176 | `cbc0b66bc15fa8fb…` |
| 123 | `outputs/q2/final/q2_rank_jump_thresholds.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 57525 | `1d7723b4c163c00c…` |
| 124 | `outputs/q2/final/q2_rank_migration.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 674 | `e47b267bb6d5548e…` |
| 125 | `outputs/q2/final/q2_rank_transition_thresholds.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 57525 | `1d7723b4c163c00c…` |
| 126 | `outputs/q2/final/q2_run_metadata.json` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 6141 | `a76cd2a276e3aa3d…` |
| 127 | `outputs/q2/final/q2_scene_rankings.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 2081 | `18732ce0c9d3e63f…` |
| 128 | `outputs/q2/final/q2_scene_scores.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 10908 | `7540c845e487fb67…` |
| 129 | `outputs/q2/final/q2_scene_weights.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 3008 | `5eb3b6871639f7f4…` |
| 130 | `outputs/q2/final/rank_migration_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 485 | `1f2277f250f30c70…` |
| 131 | `outputs/q2/final/scene_definition_audit.md` | Q2 数值结果与接口输出 | 模型假设、数据口径或稳健性说明 | 613 | `a480c08fb4928d87…` |
| 132 | `q2/data/benchmark_family_mapping.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 6008 | `7e72e42258253f42…` |
| 133 | `q2/data/q1_bt_latent_scores.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 1431 | `c901bc745d6f1755…` |
| 134 | `q2/data/q1_capability_scores.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 1315 | `dfa8e0f746277af4…` |
| 135 | `q2/data/q1_capability_scores.xlsx` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 4727 | `61195088a17c2342…` |
| 136 | `q2/data/q1_dimension_weights_reference.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 843 | `bb60462bb0e06be7…` |
| 137 | `q2/data/q1_evidence_strength.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 7117 | `3853dd8c81c52f08…` |
| 138 | `q2/data/q1_model_applicability.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 2527 | `bb62c84f2fc19c75…` |
| 139 | `q2/data/q1_model_rankings.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 1052 | `68553ece875de190…` |
| 140 | `q2/data/q1_uncertainty.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 18063 | `b170ef36ba28684c…` |
| 141 | `q2/data/q2_generation_qc.json` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 1095 | `8e5b845cc6c8864f…` |
| 142 | `q2/data/q2_model_master_table.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 6855 | `d7fa5bccbc0067fd…` |
| 143 | `q2/data/q2_model_master_table.xlsx` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 7593 | `0cf5463eeacbf58e…` |
| 144 | `q2/data/source_registry_summary.csv` | Q2 建模输入 | 模型输入、数值输出或机器可读审计 | 4472 | `04c93a0295db078c…` |
| 145 | `q2/model_spec_v1.yaml` | Q2 建模程序与规范 | Q2 KL-CES 冻结数学模型规范 | 4269 | `203f8f237d5f65f2…` |
| 146 | `q2/outputs/q2_to_q3_validation.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 1475 | `c243e207df6aaf58…` |
| 147 | `q2/outputs/scenario_utility.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 9426 | `9b2f3a00324a7525…` |
| 148 | `q2/outputs/scenario_utility_bootstrap.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 10753697 | `8a72e211892fb168…` |
| 149 | `q2/outputs/scenario_utility_summary.csv` | Q2 数值结果与接口输出 | 模型输入、数值输出或机器可读审计 | 3764 | `e08e65b666dc950a…` |
| 150 | `q3/FINAL_INPUT_AUDIT.md` | Q3 建模说明与审计 | 模型假设、数据口径或稳健性说明 | 3162 | `fc9d12566b804f7b…` |
| 151 | `q3/Q3_FINAL_AUDIT.md` | Q3 建模说明与审计 | 模型假设、数据口径或稳健性说明 | 1843 | `aecc250b40a33829…` |
| 152 | `q3/Q3_STAGE_REPORT.md` | Q3 建模说明与审计 | 模型假设、数据口径或稳健性说明 | 2163 | `bf5f8621ab6e22f8…` |
| 153 | `q3/README.md` | Q3 建模说明与审计 | 模型假设、数据口径或稳健性说明 | 1850 | `06ee88642b219072…` |
| 154 | `q3/WORKLOAD_BASELINE_JUSTIFICATION.md` | Q3 建模说明与审计 | 模型假设、数据口径或稳健性说明 | 3722 | `ae212caea2120981…` |
| 155 | `q3/data/data_dictionary.md` | Q3 建模输入与冻结数据 | 模型假设、数据口径或稳健性说明 | 2317 | `24415eedee781c26…` |
| 156 | `q3/data/fable_fallback_audit.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1622 | `cfba8f3203ef1eb2…` |
| 157 | `q3/data/model_pricing.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 7160 | `26b2533f7953bb11…` |
| 158 | `q3/data/pricing_audit.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 8231 | `733f87261c5da2ca…` |
| 159 | `q3/data/pricing_human_check.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 3474 | `f9041ea906d88d22…` |
| 160 | `q3/data/q2_interface_provenance.json` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 2455 | `452364c74f568a8d…` |
| 161 | `q3/data/q2_to_q3_interface.md` | Q3 建模输入与冻结数据 | 模型假设、数据口径或稳健性说明 | 5065 | `a86c57c77222632d…` |
| 162 | `q3/data/q2_to_q3_validation.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1456 | `714c493d930dcf6d…` |
| 163 | `q3/data/scenario_utility.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 9395 | `82bc63f0d1983775…` |
| 164 | `q3/data/scenario_utility_bootstrap.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 10693696 | `1eea0558c3df5e46…` |
| 165 | `q3/data/scenario_utility_bootstrap_template.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 98 | `14bb975d98bac8be…` |
| 166 | `q3/data/scenario_utility_summary.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 3733 | `5ff7d3311920b8f7…` |
| 167 | `q3/data/scenario_utility_template.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1432 | `3f50686b3ba08449…` |
| 168 | `q3/data/workload_config.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 4634 | `4ff34bac62395918…` |
| 169 | `q3/frozen/v1.0/Q3_FREEZE_README.md` | Q3 建模输入与冻结数据 | 模型假设、数据口径或稳健性说明 | 1197 | `483675a5def608f6…` |
| 170 | `q3/frozen/v1.0/budget_switch_points_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1391 | `1ec91f988f5d6488…` |
| 171 | `q3/frozen/v1.0/cost_performance_fit_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 4235 | `369f96d4902cfdd2…` |
| 172 | `q3/frozen/v1.0/icer_results_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1122 | `6542f0407c1c5465…` |
| 173 | `q3/frozen/v1.0/model_pricing.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 7160 | `26b2533f7953bb11…` |
| 174 | `q3/frozen/v1.0/pareto_probability_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 923 | `70a76b23a2e1f864…` |
| 175 | `q3/frozen/v1.0/pareto_results_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 2669 | `cfceda1a29582daf…` |
| 176 | `q3/frozen/v1.0/pricing_audit.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 8231 | `733f87261c5da2ca…` |
| 177 | `q3/frozen/v1.0/pricing_human_check.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 3474 | `f9041ea906d88d22…` |
| 178 | `q3/frozen/v1.0/q2_interface_provenance.json` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 2455 | `452364c74f568a8d…` |
| 179 | `q3/frozen/v1.0/q3_freeze_manifest.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 2558 | `06caba06f0ce0d71…` |
| 180 | `q3/frozen/v1.0/q3_model_analysis_cohort.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1504 | `f459dbefe78f10ac…` |
| 181 | `q3/frozen/v1.0/scenario_costs_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 5657 | `361841e1dc94f56c…` |
| 182 | `q3/frozen/v1.0/scenario_utility.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 9395 | `82bc63f0d1983775…` |
| 183 | `q3/frozen/v1.0/scenario_utility_bootstrap.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 10693696 | `1eea0558c3df5e46…` |
| 184 | `q3/frozen/v1.0/sensitivity_summary_final.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 1740 | `04c32ddce19055b4…` |
| 185 | `q3/frozen/v1.0/workload_config.csv` | Q3 建模输入与冻结数据 | 模型输入、数值输出或机器可读审计 | 4634 | `4ff34bac62395918…` |
| 186 | `q3/outputs/diagnostics/pareto_interpretation_audit.md` | Q3 数值结果与模型诊断 | 模型假设、数据口径或稳健性说明 | 2459 | `e06948a487eea247…` |
| 187 | `q3/outputs/diagnostics/q3_data_validation_report.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 716 | `75713c8f0db407ae…` |
| 188 | `q3/outputs/diagnostics/q3_freeze_manifest_audit.md` | Q3 数值结果与模型诊断 | 模型假设、数据口径或稳健性说明 | 312 | `e95199dd669b0d1b…` |
| 189 | `q3/outputs/diagnostics/q3_reproducibility_audit.md` | Q3 数值结果与模型诊断 | 模型假设、数据口径或稳健性说明 | 863 | `5bbf00fac27e6464…` |
| 190 | `q3/outputs/diagnostics/q3_run_status.json` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 1129 | `1fb89125e86f8946…` |
| 191 | `q3/outputs/tables/budget_switch_points.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 2119 | `690322a5596c6a4d…` |
| 192 | `q3/outputs/tables/budget_switch_points_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 1391 | `1ec91f988f5d6488…` |
| 193 | `q3/outputs/tables/cost_performance_fit.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 2831 | `2dcf3c7cbf95b208…` |
| 194 | `q3/outputs/tables/cost_performance_fit_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 4235 | `369f96d4902cfdd2…` |
| 195 | `q3/outputs/tables/icer_results.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 942 | `29cb3435f3109133…` |
| 196 | `q3/outputs/tables/icer_results_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 1122 | `6542f0407c1c5465…` |
| 197 | `q3/outputs/tables/pareto_probability_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 923 | `70a76b23a2e1f864…` |
| 198 | `q3/outputs/tables/pareto_results.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 5170 | `f4746fdb612e1b60…` |
| 199 | `q3/outputs/tables/pareto_results_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 2669 | `cfceda1a29582daf…` |
| 200 | `q3/outputs/tables/q3_budget_selection.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 2119 | `690322a5596c6a4d…` |
| 201 | `q3/outputs/tables/q3_cost_performance_fit.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 2831 | `2dcf3c7cbf95b208…` |
| 202 | `q3/outputs/tables/q3_cost_utility.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 4323 | `a4559b74791190fc…` |
| 203 | `q3/outputs/tables/q3_cost_utility_full_cohort.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 4323 | `a4559b74791190fc…` |
| 204 | `q3/outputs/tables/q3_incremental_cost_effectiveness.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 942 | `29cb3435f3109133…` |
| 205 | `q3/outputs/tables/q3_model_analysis_cohort.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 1504 | `f459dbefe78f10ac…` |
| 206 | `q3/outputs/tables/q3_pareto_frontier.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 5170 | `f4746fdb612e1b60…` |
| 207 | `q3/outputs/tables/q3_pareto_probability.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 776 | `a60f5cc50f197fd1…` |
| 208 | `q3/outputs/tables/q3_sensitivity_analysis.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 41305 | `d87d0ab0cbd55e4a…` |
| 209 | `q3/outputs/tables/scenario_costs.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 5808 | `7ae26c3377d22bd5…` |
| 210 | `q3/outputs/tables/scenario_costs_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 5657 | `361841e1dc94f56c…` |
| 211 | `q3/outputs/tables/sensitivity_summary_final.csv` | Q3 数值结果与模型诊断 | 模型输入、数值输出或机器可读审计 | 1740 | `04c32ddce19055b4…` |
| 212 | `q3/src/__init__.py` | Q3 建模程序 | 数学建模或模型校验源程序 | 43 | `42c19cc7943bcee1…` |
| 213 | `q3/src/budget_selection.py` | Q3 建模程序 | 预算约束最优可行模型 | 2782 | `7c82bf2ffe3d1386…` |
| 214 | `q3/src/cohort.py` | Q3 建模程序 | 数学建模或模型校验源程序 | 4804 | `ced7ec2b0ec3582a…` |
| 215 | `q3/src/cost_model.py` | Q3 建模程序 | 标准工作负载成本计算 | 3384 | `d9385455468a2401…` |
| 216 | `q3/src/cost_performance_fit.py` | Q3 建模程序 | 数学建模或模型校验源程序 | 4982 | `c990925287d55e43…` |
| 217 | `q3/src/incremental_cost.py` | Q3 建模程序 | 数学建模或模型校验源程序 | 1459 | `458519468c7e83c3…` |
| 218 | `q3/src/pareto_analysis.py` | Q3 建模程序 | 效用-成本 Pareto 前沿 | 2955 | `c7e058c2d12c57c9…` |
| 219 | `q3/src/sensitivity_analysis.py` | Q3 建模程序 | Q3 参数敏感性分析 | 4711 | `ca1693d7ac018596…` |
| 220 | `q3/src/validate_q3_data.py` | Q3 建模程序 | 数学建模或模型校验源程序 | 7057 | `6635fec3d482e131…` |
| 221 | `requirements.txt` | 复现环境 | 建模支撑材料 | 106 | `f7e6546d1ef6b187…` |
| 222 | `src/q1/__init__.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 39 | `287b5810d1dc39ef…` |
| 223 | `src/q1/bt_model.py` | Q1 建模程序 | 正则化 Bradley-Terry 潜在能力估计 | 4226 | `74dcbd877e6d6281…` |
| 224 | `src/q1/config.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 1129 | `c79f44c149cad0c2…` |
| 225 | `src/q1/correlations.py` | Q1 建模程序 | 缺失感知 Spearman 与 Family 结构 | 3513 | `41047e5f568e6693…` |
| 226 | `src/q1/dimension_weights.py` | Q1 建模程序 | 信息量、非冗余度和稳定性客观赋权 | 3562 | `decca5a849e62975…` |
| 227 | `src/q1/load_data.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 3775 | `878048e35a49770b…` |
| 228 | `src/q1/overall_score.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 2318 | `0ec0fea490ec2073…` |
| 229 | `src/q1/pairwise.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 4903 | `3e1d27324a59bd0f…` |
| 230 | `src/q1/run_q1_v12_modeling_core.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 23754 | `909d5c9ae2ced1c5…` |
| 231 | `src/q1/validate_freeze.py` | Q1 建模程序 | 数学建模或模型校验源程序 | 3801 | `fdd04bf26d65a8fb…` |
| 232 | `src/q2/__init__.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 446 | `17c3c670e946e047…` |
| 233 | `src/q2/ces.py` | Q2 建模程序与规范 | CES 场景效用函数 | 1676 | `9b43597e3d75f8f7…` |
| 234 | `src/q2/config.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 2787 | `7b00e49f7e83798c…` |
| 235 | `src/q2/data_adapter.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 6248 | `fdcfb4a5d8c3c868…` |
| 236 | `src/q2/imbalance_penalty.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 760 | `8d23e0509cb2b986…` |
| 237 | `src/q2/kl_weights.py` | Q2 建模程序与规范 | KL 最小信息投影场景权重 | 3229 | `6e40ccadad0543dc…` |
| 238 | `src/q2/linear_baseline.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 700 | `0b274f643a3bc113…` |
| 239 | `src/q2/marginal_analysis.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 2576 | `60d7bb592ad200fc…` |
| 240 | `src/q2/missing_policy.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 5026 | `c9a3f89c542ca1f0…` |
| 241 | `src/q2/normalize.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 1539 | `3a7471e8d54e8a3d…` |
| 242 | `src/q2/pairwise_analysis.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 5748 | `4b4980759e769041…` |
| 243 | `src/q2/pipeline.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 8029 | `c8afe207f85a9318…` |
| 244 | `src/q2/rank_migration.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 2811 | `20703426315f28c3…` |
| 245 | `src/q2/scene_constraints.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 5351 | `0d04a0b4749c0f36…` |
| 246 | `src/q2/sensitivity.py` | Q2 建模程序与规范 | 数学建模或模型校验源程序 | 6429 | `3ca11e43583215dc…` |

</details>

## 四、模型与数据、输出的对应关系

| 问题 | 数学模型 | 正式输入 | 数值输出 |
|---|---|---|---|
| Q1 | 缺失感知 Spearman + Family-balanced regularized Bradley--Terry + 客观赋权 | `frozen/v1.0/` | `outputs/q1_v1.2/results_summary_v1.2.json`、敏感性 CSV、结果表 |
| Q2 | KL 最小信息投影 + CES 互补效用 | `q2/data/`、`q2/model_spec_v1.yaml` | `outputs/q2/final/*.csv`、`q2/outputs/scenario_utility*.csv` |
| Q3 | 工作负载成本 + Pareto + 预算约束选择 | `q3/frozen/v1.0/` | `q3/outputs/tables/*_final.csv`、模型诊断 |

## 五、数学建模源程序

下面列出 Q1--Q3 数学计算模块。`src/q1/run_q1_v12_modeling_core.py` 汇集 Q1 主流程中的 17 个数学函数，函数体逐字源于正式入口 `src/q1/run_q1_v12.py`，并配有必要的数值计算导入与原有常量。Q2、Q3 按数学模块完整列出。

## 5.1 Q1 基础数学模块

这些完整数学模块负责冻结数据读取、缺失感知相关性、成对关系、BT 估计、客观权重、综合得分、Bootstrap、LOFO/LOSO、等权敏感性与冻结校验。`run_q1_v12_modeling_core.py` 的函数体逐字源于 Q1 v1.2 正式入口。

### `src/q1/__init__.py`

~~~~python
"""Question 1 modeling pipeline."""
~~~~

### `src/q1/config.py`

~~~~python
from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FROZEN_DIR = ROOT / "frozen" / "v1.0"
OUTPUT_DIR = ROOT / "outputs" / "q1"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
DIAG_DIR = OUTPUT_DIR / "diagnostics"
BOOT_DIR = OUTPUT_DIR / "bootstrap"
LOG_DIR = OUTPUT_DIR / "logs"

FREEZE_VERSION = "v1.0"
FREEZE_DATE = "2026-08-17"
RANDOM_SEED = 20260817
MAIN_LAMBDA = 1.0
LAMBDA_GRID = [0.1, 0.3, 1.0, 3.0, 10.0]
MARGIN_EPSILON = 0.1
REDUNDANCY_THRESHOLDS = [0.80, 0.85, 0.90]
DEFAULT_BOOTSTRAP_B = int(os.environ.get("Q1_BOOTSTRAP_B", "2000"))

CORE_MODELS = [
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "deepseek_v4_pro_max",
    "deepseek_v4_flash_max",
    "qwen3_8_max",
    "glm_5_2_max",
]

KIMI_MODEL_ID = "kimi_k3_max"


def ensure_output_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, DIAG_DIR, BOOT_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)
~~~~

### `src/q1/load_data.py`

~~~~python
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import CORE_MODELS, FROZEN_DIR


@dataclass(frozen=True)
class Q1Data:
    models: pd.DataFrame
    manifest: pd.DataFrame
    family_manifest: pd.DataFrame
    matrix: pd.DataFrame
    raw: pd.DataFrame
    selected: pd.DataFrame
    long: pd.DataFrame
    dimensions: list[str]
    families: list[str]
    settings: list[str]
    model_names: dict[str, str]


def _bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper().isin({"TRUE", "1", "YES"})


def load_q1_data() -> Q1Data:
    models = pd.read_excel(FROZEN_DIR / "model_pool_v1.0.xlsx", sheet_name="Models")
    manifest = pd.read_excel(FROZEN_DIR / "final_modeling_benchmark_manifest_v1.0.xlsx", sheet_name="Manifest")
    family_manifest = pd.read_excel(FROZEN_DIR / "benchmark_family_manifest_v1.0.xlsx", sheet_name="Families")
    matrix = pd.read_excel(FROZEN_DIR / "final_modeling_matrix_v1.0.xlsx", sheet_name="Matrix")
    raw = pd.read_excel(FROZEN_DIR / "raw_benchmark_data_v1.0.xlsx", sheet_name="RawData")

    selected = raw[_bool_series(raw["selected_for_final_modeling"])].copy()
    selected["score"] = pd.to_numeric(selected["raw_score"], errors="coerce")
    selected["applicable"] = selected["score"].notna()
    selected["human_verified_bool"] = _bool_series(selected["human_verified"])
    selected["higher_is_better_bool"] = _bool_series(selected["higher_is_better"])

    manifest = manifest.rename(columns={"capability": "dimension", "selected_setting": "setting_id"}).copy()
    selected = selected.merge(
        manifest[
            [
                "dimension",
                "benchmark_family",
                "setting_id",
                "family_weight_within_capability",
                "setting_weight_within_family",
                "network_contribution",
                "redundancy_status",
            ]
        ],
        left_on=["capability_dimension", "benchmark_family", "setting_id"],
        right_on=["dimension", "benchmark_family", "setting_id"],
        how="left",
        suffixes=("", "_manifest"),
    )
    selected["dimension"] = selected["dimension"].fillna(selected["capability_dimension"])

    long = selected[
        [
            "model_id",
            "model_full_name",
            "dimension",
            "benchmark_family",
            "setting_id",
            "score",
            "applicable",
            "source_id",
            "human_verified_bool",
            "higher_is_better_bool",
            "family_weight_within_capability",
            "setting_weight_within_family",
        ]
    ].copy()
    long = long.rename(columns={"human_verified_bool": "human_verified", "higher_is_better_bool": "higher_is_better"})

    model_order = {model_id: i for i, model_id in enumerate(CORE_MODELS)}
    models = models[models["model_id"].isin(CORE_MODELS)].copy()
    models["_order"] = models["model_id"].map(model_order)
    models = models.sort_values("_order").drop(columns="_order")

    settings = manifest["setting_id"].drop_duplicates().tolist()
    dimensions = manifest["dimension"].drop_duplicates().tolist()
    families = manifest["benchmark_family"].drop_duplicates().tolist()
    model_names = dict(zip(models["model_id"], models["model_full_name"]))

    return Q1Data(
        models=models,
        manifest=manifest,
        family_manifest=family_manifest,
        matrix=matrix,
        raw=raw,
        selected=selected,
        long=long,
        dimensions=dimensions,
        families=families,
        settings=settings,
        model_names=model_names,
    )
~~~~

### `src/q1/correlations.py`

~~~~python
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def setting_rank_table(long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for setting_id, group in long.groupby("setting_id", sort=False):
        values = group.dropna(subset=["score"]).copy()
        if values.empty:
            continue
        ascending = not bool(values["higher_is_better"].iloc[0])
        values["setting_rank_score"] = values["score"].rank(method="average", pct=True, ascending=ascending)
        rows.append(values[["model_id", "dimension", "benchmark_family", "setting_id", "setting_rank_score"]])
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def family_representation(long: pd.DataFrame) -> pd.DataFrame:
    ranked = setting_rank_table(long)
    family_scores = (
        ranked.groupby(["model_id", "dimension", "benchmark_family"], as_index=False)["setting_rank_score"]
        .mean()
        .rename(columns={"setting_rank_score": "family_score"})
    )
    return family_scores.pivot(index="model_id", columns="benchmark_family", values="family_score")


def missing_aware_spearman(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = list(table.columns)
    corr = pd.DataFrame(np.nan, index=cols, columns=cols, dtype=float)
    common_n = pd.DataFrame(0, index=cols, columns=cols, dtype=int)
    for a in cols:
        for b in cols:
            common = table[[a, b]].dropna()
            common_n.loc[a, b] = len(common)
            if a == b and len(common) > 0:
                corr.loc[a, b] = 1.0
            elif len(common) >= 3 and common[a].nunique() > 1 and common[b].nunique() > 1:
                rho = spearmanr(common[a], common[b]).correlation
                corr.loc[a, b] = float(rho) if np.isfinite(rho) else np.nan
    return corr, common_n


def family_screening(long: pd.DataFrame, corr: pd.DataFrame, common_n: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    coverage = (
        long.groupby(["dimension", "benchmark_family"])["score"]
        .apply(lambda s: float(s.notna().mean()))
        .reset_index(name="coverage")
    )
    rows = []
    for row in coverage.itertuples(index=False):
        fam = row.benchmark_family
        vals = corr.loc[fam].drop(labels=[fam], errors="ignore").abs().dropna()
        max_abs = float(vals.max()) if len(vals) else np.nan
        if len(vals):
            partner = vals.idxmax()
            n_val = int(common_n.loc[fam, partner])
        else:
            partner = ""
            n_val = 0
        flag = bool(np.isfinite(max_abs) and max_abs >= threshold)
        settings = long.loc[long["benchmark_family"].eq(fam), "setting_id"].nunique()
        network_role = "STRUCTURAL_BRIDGE" if row.coverage < 0.5 or settings == 1 else "STANDARD_INFORMATION"
        reason = "Retained: frozen v1.0 formal family mapping is fixed; redundancy is reported, not silently removed."
        rows.append(
            {
                "dimension": row.dimension,
                "benchmark_family": fam,
                "coverage": row.coverage,
                "max_abs_spearman": max_abs,
                "highest_corr_partner": partner,
                "common_n": n_val,
                "redundancy_flag": flag,
                "network_role": network_role,
                "retain_reason": reason,
            }
        )
    return pd.DataFrame(rows)
~~~~

### `src/q1/pairwise.py`

~~~~python
from __future__ import annotations

from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd


def _margin_scale(scores: pd.Series, method: str) -> float:
    if method == "robust_iqr":
        q75, q25 = np.nanpercentile(scores, [75, 25])
        scale = q75 - q25
    else:
        scale = float(np.nanmax(scores) - np.nanmin(scores))
    return scale if np.isfinite(scale) and scale > 0 else 1.0


def build_pairwise(
    long: pd.DataFrame,
    dimension: str | None = None,
    margin_method: str = "range",
    epsilon_m: float = 0.1,
    exclude_families: set[str] | None = None,
) -> pd.DataFrame:
    data = long.copy()
    if dimension is not None:
        data = data[data["dimension"].eq(dimension)].copy()
    if exclude_families:
        data = data[~data["benchmark_family"].isin(exclude_families)].copy()
    rows = []
    family_counts = data.groupby("dimension")["benchmark_family"].nunique().to_dict()
    setting_counts = data.groupby(["dimension", "benchmark_family"])["setting_id"].nunique().to_dict()
    for (dim, family, setting_id), group in data.groupby(["dimension", "benchmark_family", "setting_id"], sort=False):
        values = group.dropna(subset=["score"]).copy()
        if len(values) < 2:
            continue
        ascending = not bool(values["higher_is_better"].iloc[0])
        scale = _margin_scale(values["score"], margin_method)
        raw_rows = []
        for a, b in combinations(values.itertuples(index=False), 2):
            diff = float(a.score) - float(b.score)
            if not bool(a.higher_is_better):
                diff = -diff
            if diff > 0:
                y = 1.0
            elif diff < 0:
                y = 0.0
            else:
                y = 0.5
            if margin_method == "none":
                raw_weight = 1.0
            else:
                margin = min(abs(float(a.score) - float(b.score)) / scale, 1.0)
                raw_weight = epsilon_m + (1.0 - epsilon_m) * margin
            raw_rows.append(
                {
                    "dimension": dim,
                    "benchmark_family": family,
                    "setting_id": setting_id,
                    "model_i": a.model_id,
                    "model_j": b.model_id,
                    "y": y,
                    "raw_margin_weight": raw_weight,
                    "score_i": float(a.score),
                    "score_j": float(b.score),
                }
            )
        raw_total = sum(r["raw_margin_weight"] for r in raw_rows)
        family_total = 1.0 / family_counts[dim]
        setting_total = family_total / setting_counts[(dim, family)]
        for item in raw_rows:
            item["weight"] = item["raw_margin_weight"] / raw_total * setting_total if raw_total else 0.0
            rows.append(item)
    return pd.DataFrame(rows)


def graph_diagnostics(pairwise: pd.DataFrame, all_models: list[str]) -> dict[str, object]:
    graph = nx.Graph()
    graph.add_nodes_from(all_models)
    for row in pairwise.itertuples(index=False):
        graph.add_edge(row.model_i, row.model_j)
    components = [sorted(c) for c in nx.connected_components(graph)]
    largest = max((len(c) for c in components), default=0)
    active = sorted(set(pairwise["model_i"]).union(set(pairwise["model_j"]))) if len(pairwise) else []
    active_graph = graph.subgraph(active).copy()
    active_components = [sorted(c) for c in nx.connected_components(active_graph)] if active else []
    active_largest = max((len(c) for c in active_components), default=0)
    return {
        "connected": bool(nx.is_connected(active_graph)) if len(active_graph) > 0 else False,
        "largest_connected_component": int(active_largest),
        "active_models": active,
        "components": active_components,
        "all_model_largest_component": int(largest),
    }


def pairwise_diagnostics(pairwise: pd.DataFrame, all_models: list[str]) -> pd.DataFrame:
    rows = []
    if pairwise.empty:
        return pd.DataFrame()
    for (dim, fam, setting), group in pairwise.groupby(["dimension", "benchmark_family", "setting_id"], sort=False):
        diag = graph_diagnostics(group, all_models)
        rows.append(
            {
                "dimension": dim,
                "family": fam,
                "setting": setting,
                "pairwise_comparison_count": len(group),
                "total_raw_margin_weight": float(group["raw_margin_weight"].sum()),
                "balanced_total_weight": float(group["weight"].sum()),
                "participating_models": "; ".join(diag["active_models"]),
                "comparison_graph_connectivity": "CONNECTED" if diag["connected"] else "PARTIAL_OR_SINGLE_SETTING",
            }
        )
    return pd.DataFrame(rows)
~~~~

### `src/q1/bt_model.py`

~~~~python
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, log_expit


def separation_warning(pairwise: pd.DataFrame, models: list[str]) -> bool:
    if pairwise.empty:
        return False
    wins = {m: 0.0 for m in models}
    losses = {m: 0.0 for m in models}
    for row in pairwise.itertuples(index=False):
        if row.y > 0.5:
            wins[row.model_i] += row.weight
            losses[row.model_j] += row.weight
        elif row.y < 0.5:
            wins[row.model_j] += row.weight
            losses[row.model_i] += row.weight
    active = [m for m in models if wins[m] + losses[m] > 0]
    return any((wins[m] == 0.0 or losses[m] == 0.0) for m in active)


def fit_bt(pairwise: pd.DataFrame, models: list[str], lambda_: float = 1.0) -> dict[str, object]:
    active = sorted(set(pairwise["model_i"]).union(set(pairwise["model_j"])), key=models.index) if len(pairwise) else []
    if len(active) < 2:
        return {
            "theta": {m: np.nan for m in models},
            "converged": False,
            "message": "Fewer than two active models",
            "n_iter": 0,
            "objective": np.nan,
            "separation_warning": False,
        }
    index = {m: i for i, m in enumerate(active)}
    i_idx = pairwise["model_i"].map(index).to_numpy()
    j_idx = pairwise["model_j"].map(index).to_numpy()
    y = pairwise["y"].astype(float).to_numpy()
    w = pairwise["weight"].astype(float).to_numpy()
    n = len(active)

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        delta = theta[i_idx] - theta[j_idx]
        p = expit(delta)
        # -[y log(sigmoid(delta)) + (1-y) log(sigmoid(-delta))]
        nll = -np.sum(w * (y * log_expit(delta) + (1.0 - y) * log_expit(-delta)))
        nll += 0.5 * lambda_ * float(np.dot(theta, theta))
        grad = np.zeros(n)
        g = w * (p - y)
        np.add.at(grad, i_idx, g)
        np.add.at(grad, j_idx, -g)
        grad += lambda_ * theta
        return float(nll), grad

    result = minimize(lambda t: objective(t), np.zeros(n), jac=True, method="L-BFGS-B", options={"maxiter": 500})
    theta = result.x - result.x.mean()
    theta_map = {m: np.nan for m in models}
    theta_map.update({m: float(theta[index[m]]) for m in active})
    return {
        "theta": theta_map,
        "converged": bool(result.success),
        "message": str(result.message),
        "n_iter": int(result.nit),
        "objective": float(result.fun) if math.isfinite(float(result.fun)) else np.nan,
        "separation_warning": separation_warning(pairwise, models),
    }


def score_dimension(pairwise: pd.DataFrame, models: list[str], dimension: str, lambda_: float) -> tuple[pd.DataFrame, dict[str, object]]:
    fit = fit_bt(pairwise, models=models, lambda_=lambda_)
    theta = pd.Series(fit["theta"], name="theta", dtype=float)
    available = theta.notna()
    scores = pd.Series(np.nan, index=theta.index, dtype=float, name="score")
    if available.sum() >= 2:
        values = theta[available]
        spread = values.max() - values.min()
        if spread > 0:
            scores.loc[available] = 100.0 * (values - values.min()) / spread
        else:
            scores.loc[available] = 50.0
    out = pd.DataFrame(
        {
            "model_id": theta.index,
            f"{dimension}_theta": theta.values,
            f"{dimension}_score": scores.values,
            f"{dimension}_applicable": available.values,
        }
    )
    return out, fit


def fit_dimensions(
    pairwise: pd.DataFrame,
    dimensions: list[str],
    models: list[str],
    lambda_: float,
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    base = pd.DataFrame({"model_id": models})
    diagnostics: dict[str, dict[str, object]] = {}
    for dim in dimensions:
        dim_pw = pairwise[pairwise["dimension"].eq(dim)].copy()
        dim_score, fit = score_dimension(dim_pw, models, dim, lambda_)
        base = base.merge(dim_score, on="model_id", how="left")
        diagnostics[dim] = fit
    return base, diagnostics
~~~~

### `src/q1/dimension_weights.py`

~~~~python
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def dimension_score_matrix(dimension_scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=dimension_scores["model_id"])
    for dim in dimensions:
        out[dim] = dimension_scores[f"{dim}_score"].to_numpy()
    return out


def information_factor(scores: pd.Series, eps: float = 1e-9) -> float:
    values = scores.dropna().astype(float)
    n = len(values)
    if n <= 1:
        return 0.0
    shifted = values - min(0.0, values.min()) + eps
    total = shifted.sum()
    if total <= 0:
        return 0.0
    p = shifted / total
    entropy = -float(np.sum(p * np.log(p))) / np.log(n)
    return float(np.clip(1.0 - entropy, 0.0, 1.0))


def non_redundancy_factors(score_matrix: pd.DataFrame) -> dict[str, float]:
    out = {}
    for dim in score_matrix.columns:
        corrs = []
        for other in score_matrix.columns:
            if other == dim:
                continue
            common = score_matrix[[dim, other]].dropna()
            if len(common) >= 3 and common[dim].nunique() > 1 and common[other].nunique() > 1:
                rho = spearmanr(common[dim], common[other]).correlation
                if np.isfinite(rho):
                    corrs.append(abs(float(rho)))
        out[dim] = float(np.clip(1.0 - np.mean(corrs), 0.0, 1.0)) if corrs else 1.0
    return out


def stability_factors(
    dimensions: list[str],
    bootstrap_dimension_scores: pd.DataFrame | None = None,
) -> dict[str, float]:
    if bootstrap_dimension_scores is None or bootstrap_dimension_scores.empty:
        return {dim: 1.0 for dim in dimensions}
    uncertainty = {}
    for dim in dimensions:
        col = f"{dim}_score"
        if col not in bootstrap_dimension_scores:
            uncertainty[dim] = np.nan
            continue
        sd_by_model = bootstrap_dimension_scores.groupby("model_id")[col].std().dropna()
        uncertainty[dim] = float(sd_by_model.median()) if len(sd_by_model) else np.nan
    finite = [v for v in uncertainty.values() if np.isfinite(v)]
    denom = float(np.median(finite)) if finite and np.median(finite) > 0 else 1.0
    return {
        dim: float(1.0 / (1.0 + ((uncertainty[dim] / denom) if np.isfinite(uncertainty[dim]) else 1.0)))
        for dim in dimensions
    }


def compute_dimension_weights(
    dimension_scores: pd.DataFrame,
    dimensions: list[str],
    bootstrap_dimension_scores: pd.DataFrame | None = None,
    stability_override: dict[str, float] | None = None,
) -> pd.DataFrame:
    score_matrix = dimension_score_matrix(dimension_scores, dimensions)
    info = {dim: information_factor(score_matrix[dim]) for dim in dimensions}
    nonred = non_redundancy_factors(score_matrix)
    stability = stability_override or stability_factors(dimensions, bootstrap_dimension_scores)
    rows = []
    for dim in dimensions:
        raw = info[dim] * nonred[dim] * stability[dim]
        rows.append(
            {
                "dimension": dim,
                "information": info[dim],
                "non_redundancy": nonred[dim],
                "stability": stability[dim],
                "raw_weight": raw,
            }
        )
    out = pd.DataFrame(rows)
    total = out["raw_weight"].sum()
    if total <= 0:
        out["final_weight"] = 1.0 / len(out)
    else:
        out["final_weight"] = out["raw_weight"] / total
    return out
~~~~

### `src/q1/overall_score.py`

~~~~python
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_overall_scores(
    dimension_scores: pd.DataFrame,
    weights: pd.DataFrame,
    dimensions: list[str],
    model_names: dict[str, str],
    model_subset: set[str] | None = None,
) -> pd.DataFrame:
    weight_map = dict(zip(weights["dimension"], weights["final_weight"]))
    rows = []
    for _, row in dimension_scores.iterrows():
        model_id = row["model_id"]
        if model_subset is not None and model_id not in model_subset:
            continue
        numerator = 0.0
        denominator = 0.0
        available = 0
        values = {}
        for dim in dimensions:
            score = row[f"{dim}_score"]
            values[f"{dim}_score"] = score
            if pd.notna(score):
                numerator += weight_map[dim] * float(score)
                denominator += weight_map[dim]
                available += 1
        overall = numerator / denominator if denominator > 0 else np.nan
        rows.append(
            {
                "model_id": model_id,
                "model": model_names.get(model_id, model_id),
                "overall_score": overall,
                "effective_weight_coverage": denominator,
                "number_of_available_dimensions": available,
                **values,
            }
        )
    out = pd.DataFrame(rows).sort_values(["overall_score", "effective_weight_coverage"], ascending=[False, False])
    out["rank"] = range(1, len(out) + 1)
    cols = ["rank", "model_id", "model", "overall_score", "effective_weight_coverage", "number_of_available_dimensions"]
    score_cols = [f"{dim}_score" for dim in dimensions]
    return out[cols + score_cols]


def rerank_with_dimensions(
    dimension_scores: pd.DataFrame,
    weights: pd.DataFrame,
    keep_dimensions: list[str],
    all_dimensions: list[str],
    model_names: dict[str, str],
    model_subset: set[str] | None = None,
) -> pd.DataFrame:
    sub_weights = weights[weights["dimension"].isin(keep_dimensions)].copy()
    sub_weights["final_weight"] = sub_weights["final_weight"] / sub_weights["final_weight"].sum()
    return compute_overall_scores(dimension_scores, sub_weights, keep_dimensions, model_names, model_subset=model_subset)
~~~~

### `src/q1/validate_freeze.py`

~~~~python
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .config import FREEZE_DATE, FREEZE_VERSION, FROZEN_DIR


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sha256(frozen_dir: Path = FROZEN_DIR) -> dict[str, object]:
    sums = frozen_dir / "SHA256SUMS_v1.0.txt"
    if not sums.exists():
        raise FileNotFoundError(f"Missing freeze checksum file: {sums}")
    mismatches: list[dict[str, str]] = []
    checked = 0
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split("  ", 1)
        target = frozen_dir / filename
        actual = sha256(target) if target.exists() else "MISSING"
        checked += 1
        if actual != expected:
            mismatches.append({"filename": filename, "expected": expected, "actual": actual})
    if mismatches:
        raise ValueError(f"SHA-256 validation failed: {mismatches}")
    return {"checked_files": checked, "sha256_passed": True}


def validate_freeze_state(frozen_dir: Path = FROZEN_DIR) -> dict[str, object]:
    checksum = validate_sha256(frozen_dir)
    matrix = pd.read_excel(frozen_dir / "final_modeling_matrix_v1.0.xlsx", sheet_name="Matrix")
    raw = pd.read_excel(frozen_dir / "raw_benchmark_data_v1.0.xlsx", sheet_name="RawData")
    manifest = pd.read_excel(frozen_dir / "final_modeling_benchmark_manifest_v1.0.xlsx", sheet_name="Manifest")
    models = pd.read_excel(frozen_dir / "model_pool_v1.0.xlsx", sheet_name="Models")
    gate = pd.read_excel(frozen_dir / "modeling_readiness_gate_v1.0.xlsx", sheet_name="Gate")

    selected = raw[raw["selected_for_final_modeling"].astype(str).str.upper().eq("TRUE")].copy()
    setting_cols = [c for c in matrix.columns if str(c).startswith("S_")]
    observed = {
        "core_models": int(models["role"].astype(str).eq("CORE_MODEL").sum()),
        "benchmark_families": int(manifest["benchmark_family"].nunique()),
        "exact_settings": int(manifest["selected_setting"].nunique()),
        "theoretical_cells": int(len(models) * len(setting_cols)),
        "nonmissing_core_records": int(matrix[setting_cols].notna().sum().sum()),
        "overall_coverage": float(matrix[setting_cols].notna().sum().sum() / (len(models) * len(setting_cols))),
        "human_verified_true": int(selected["human_verified"].astype(str).str.upper().eq("TRUE").sum()),
        "human_verified_false": int(selected["human_verified"].astype(str).str.upper().eq("FALSE").sum()),
        "traceability": 1.0,
        "freeze_version": str(gate["data_freeze_version"].dropna().iloc[0]),
        "freeze_date": str(pd.to_datetime(gate["data_freeze_date"].dropna().iloc[0]).date()),
    }
    expected = {
        "core_models": 10,
        "benchmark_families": 14,
        "exact_settings": 21,
        "theoretical_cells": 210,
        "nonmissing_core_records": 164,
        "human_verified_true": 164,
        "human_verified_false": 0,
        "freeze_version": FREEZE_VERSION,
        "freeze_date": FREEZE_DATE,
    }
    failures = {
        key: {"observed": observed[key], "expected": value}
        for key, value in expected.items()
        if observed[key] != value
    }
    if round(observed["overall_coverage"], 4) != 0.7810:
        failures["overall_coverage"] = {"observed": observed["overall_coverage"], "expected": 0.7810}
    if failures:
        raise ValueError(f"Frozen v1.0 validation failed: {failures}")
    observed.update(checksum)
    return observed
~~~~

### `src/q1/run_q1_v12_modeling_core.py`

~~~~python
from __future__ import annotations

"""Q1 v1.2 mathematical-modeling core.

This derivative module was mechanically extracted from ``src/q1/run_q1_v12.py``.
The listed mathematical function bodies are verbatim, with their required
numerical imports and original constants.
"""

import os
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import kendalltau, spearmanr

from .bt_model import fit_dimensions
from .config import CORE_MODELS, KIMI_MODEL_ID, MAIN_LAMBDA, MARGIN_EPSILON
from .correlations import family_representation, missing_aware_spearman
from .dimension_weights import information_factor, non_redundancy_factors
from .load_data import Q1Data
from .pairwise import build_pairwise, graph_diagnostics


RANDOM_SEED = 20260817
BOOTSTRAP_B = int(os.environ.get("Q1_V12_BOOTSTRAP_B", "2000"))

TYPE_C_MODELS = {
    "kimi_k3_max",
    "gpt_5_6_sol_max",
    "gpt_5_5_xhigh",
    "claude_fable_5_max",
    "claude_opus_4_8_max",
    "gemini_3_1_pro_high",
    "qwen3_8_max",
}
TYPE_A_MODELS = {"deepseek_v4_pro_max", "deepseek_v4_flash_max", "glm_5_2_max"}


def dim_code(dimension: str) -> str:
    return dimension.split(" ", 1)[0]

def c5_audit(q1: Q1Data) -> pd.DataFrame:
    c5 = q1.long[q1.long["dimension"].str.startswith("C5")]
    rows = []
    for model_id in CORE_MODELS:
        name = q1.model_names[model_id]
        observed = set(c5.loc[(c5["model_id"] == model_id) & c5["score"].notna(), "benchmark_family"])
        if model_id in TYPE_C_MODELS:
            capable: bool | str = True
            kind = "Type C: NORMAL_OBSERVATION"
            rule = "Use observed C5 Bradley-Terry score as S_i5*."
            evidence = "Frozen C5 observation(s): " + ", ".join(sorted(observed))
        elif model_id in TYPE_A_MODELS:
            capable = False
            kind = "Type A: STRUCTURAL_CAPABILITY_ABSENCE"
            rule = "Benchmark scores remain NA; set capability availability A_i=0 and S_i5*=0 only for the overall capability system."
            if model_id == "glm_5_2_max":
                evidence = "Manual capability verification v1.2; reviewer-confirmed GLM-5.2 (max) has no native multimodal capability under the problem definition."
            else:
                evidence = (
                    "SRC003 DeepSeek-V4 official technical report, line 3348: "
                    "'We are also working on incorporating multimodal capabilities to our models.'"
                )
        else:
            capable = False
            kind = "Type A: STRUCTURAL_CAPABILITY_ABSENCE"
            rule = "Benchmark scores remain NA; set capability availability A_i=0 and S_i5*=0 only for the overall capability system."
            evidence = (
                "Manual capability verification v1.2; official GLM-5.2 model capability documentation and comparison evidence; "
                "reviewer-confirmed native multimodal capability is absent."
            )
        if model_id in TYPE_C_MODELS:
            mmmu = "OBSERVED" if "MMMU-Pro" in observed else "BENCHMARK_MISSING"
            mathvision = "OBSERVED" if "MathVision" in observed else "BENCHMARK_MISSING"
        elif model_id in TYPE_A_MODELS:
            mmmu = mathvision = "NOT_APPLICABLE_CAPABILITY_ABSENCE"
        else:
            mmmu = mathvision = "NOT_APPLICABLE_CAPABILITY_ABSENCE"
        rows.append(
            {
                "model_id": model_id,
                "model": name,
                "multimodal_capable": capable,
                "C5_applicability_type": kind,
                "MMMU_Pro_status": mmmu,
                "MathVision_status": mathvision,
                "evidence_source": evidence,
                "handling_rule": rule,
            }
        )
    return pd.DataFrame(rows)

def fit_main(q1: Q1Data, long: pd.DataFrame) -> dict[str, Any]:
    pairwise = build_pairwise(long, margin_method="range", epsilon_m=MARGIN_EPSILON)
    scores, diag = fit_dimensions(pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
    return {"pairwise": pairwise, "scores": scores, "diag": diag}

def score_matrix(scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    matrix = scores.set_index("model_id")[[f"{d}_score" for d in dimensions]].copy()
    matrix.columns = [dim_code(d) for d in dimensions]
    return matrix

def theta_matrix(scores: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    matrix = scores.set_index("model_id")[[f"{d}_theta" for d in dimensions]].copy()
    matrix.columns = [dim_code(d) for d in dimensions]
    return matrix

def perspective_matrix(scores: pd.DataFrame, dimensions: list[str], perspective: str) -> pd.DataFrame:
    base = score_matrix(scores, dimensions)
    if perspective == "A":
        out = base.loc[CORE_MODELS, ["C1", "C2", "C3", "C4", "C5"]].copy()
        out.loc[list(TYPE_A_MODELS), "C5"] = 0.0
        return out
    if perspective == "B":
        return base.loc[CORE_MODELS, ["C1", "C2", "C3", "C4"]].copy()
    if perspective == "C":
        return base.loc[[m for m in CORE_MODELS if m in TYPE_C_MODELS], ["C1", "C2", "C3", "C4", "C5"]].copy()
    raise ValueError(perspective)

def stability_from_boot_theta(
    main_theta: pd.DataFrame,
    boot_theta_long: pd.DataFrame,
    model_subset: list[str],
    dimensions: list[str],
) -> tuple[dict[str, float], pd.DataFrame]:
    rows = []
    factors: dict[str, float] = {}
    for dim in dimensions:
        code = dim_code(dim)
        reference = main_theta.loc[main_theta.index.intersection(model_subset), code].dropna()
        rhos = []
        for _, group in boot_theta_long[boot_theta_long["dimension"] == code].groupby("bootstrap"):
            candidate = group.set_index("model_id")["theta"]
            common = reference.index.intersection(candidate.dropna().index)
            if len(common) >= 3 and reference.loc[common].nunique() > 1 and candidate.loc[common].nunique() > 1:
                rho = spearmanr(reference.loc[common], candidate.loc[common]).correlation
                if np.isfinite(rho):
                    rhos.append(float(rho))
        median_rho = float(np.median(rhos)) if rhos else np.nan
        stability = float((1.0 + median_rho) / 2.0) if np.isfinite(median_rho) else 0.5
        factors[code] = stability
        rows.append(
            {
                "perspective_dimension": code,
                "valid_bootstrap_replicates": len(rhos),
                "median_spearman_theta_rank": median_rho,
                "latent_ranking_stability_T": stability,
            }
        )
    return factors, pd.DataFrame(rows)

def objective_weights(matrix: pd.DataFrame, stability: dict[str, float]) -> pd.DataFrame:
    info = {c: information_factor(matrix[c]) for c in matrix.columns}
    nonred = non_redundancy_factors(matrix)
    rows = []
    for code in matrix.columns:
        raw = info[code] * nonred[code] * stability[code]
        rows.append(
            {
                "dimension": code,
                "information_I": info[code],
                "non_redundancy_R": nonred[code],
                "latent_rank_stability_T": stability[code],
                "q": raw,
            }
        )
    out = pd.DataFrame(rows)
    total = float(out["q"].sum())
    out["weight"] = out["q"] / total if total > 0 else 1.0 / len(out)
    return out

def rank_matrix(matrix: pd.DataFrame, weights: pd.DataFrame, q1: Q1Data, label: str) -> pd.DataFrame:
    if matrix.isna().any(axis=None):
        bad = matrix.index[matrix.isna().any(axis=1)].tolist()
        raise ValueError(f"{label} contains incomplete rows: {bad}")
    weight_map = weights.set_index("dimension")["weight"].reindex(matrix.columns)
    scores = matrix.mul(weight_map, axis=1).sum(axis=1)
    out = matrix.copy()
    # The matrix index is the model id; clear its name before adding the
    # explicit model_id column so pandas does not see an ambiguous label.
    out.index.name = None
    out.insert(0, "model", [q1.model_names[m] for m in out.index])
    out.insert(0, "model_id", out.index)
    out["overall_score"] = scores
    out = out.sort_values(["overall_score", "model_id"], ascending=[False, True]).reset_index(drop=True)
    out.insert(0, "rank", np.arange(1, len(out) + 1))
    out["ranking_perspective"] = label
    return out

def rank_comparison(main: pd.DataFrame, other: pd.DataFrame, label: str) -> dict[str, Any]:
    merged = main[["model_id", "rank"]].merge(other[["model_id", "rank"]], on="model_id", suffixes=("_A", "_other"))
    rho = spearmanr(merged["rank_A"], merged["rank_other"]).correlation if len(merged) >= 3 else np.nan
    tau = kendalltau(merged["rank_A"], merged["rank_other"]).correlation if len(merged) >= 3 else np.nan
    a_top3 = set(main.nsmallest(3, "rank")["model_id"])
    o_top3 = set(other.nsmallest(3, "rank")["model_id"])
    kimi_a = main.loc[main["model_id"] == KIMI_MODEL_ID, "rank"]
    kimi_o = other.loc[other["model_id"] == KIMI_MODEL_ID, "rank"]
    return {
        "comparison": label,
        "common_models": len(merged),
        "spearman": float(rho) if np.isfinite(rho) else np.nan,
        "kendall_tau": float(tau) if np.isfinite(tau) else np.nan,
        "kimi_rank_A": int(kimi_a.iloc[0]) if len(kimi_a) else np.nan,
        "kimi_rank_other": int(kimi_o.iloc[0]) if len(kimi_o) else np.nan,
        "top3_overlap_count": len(a_top3 & o_top3),
        "top3_membership_A": "; ".join(sorted(a_top3)),
        "top3_membership_other": "; ".join(sorted(o_top3)),
    }

def parametric_bootstrap(
    q1: Q1Data,
    pairwise: pd.DataFrame,
    main_scores: pd.DataFrame,
    b: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    main_theta = theta_matrix(main_scores, q1.dimensions)
    p = []
    for row in pairwise.itertuples(index=False):
        code = dim_code(row.dimension)
        delta = main_theta.loc[row.model_i, code] - main_theta.loc[row.model_j, code]
        p.append(float(expit(delta)))
    p = np.asarray(p)
    theta_rows = []
    score_rows = []
    convergence_rows = []
    for iteration in range(1, b + 1):
        boot_pairwise = pairwise.copy()
        boot_pairwise["y"] = rng.binomial(1, p).astype(float)
        scores, diag = fit_dimensions(boot_pairwise, q1.dimensions, CORE_MODELS, MAIN_LAMBDA)
        for dim in q1.dimensions:
            code = dim_code(dim)
            for row in scores[["model_id", f"{dim}_theta", f"{dim}_score"]].itertuples(index=False):
                theta_rows.append({"bootstrap": iteration, "dimension": code, "model_id": row[0], "theta": row[1]})
                score_rows.append({"bootstrap": iteration, "dimension": code, "model_id": row[0], "score": row[2]})
            convergence_rows.append(
                {
                    "bootstrap": iteration,
                    "dimension": code,
                    "converged": bool(diag[dim]["converged"]),
                    "message": diag[dim]["message"],
                }
            )
        if iteration % 100 == 0:
            print(f"q1_v1.2 bootstrap {iteration}/{b}", flush=True)
    return pd.DataFrame(theta_rows), pd.DataFrame(score_rows), pd.DataFrame(convergence_rows)

def bootstrap_perspective_scores(
    q1: Q1Data,
    boot_score_long: pd.DataFrame,
    stability: dict[str, float],
    perspective: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rank_rows = []
    weight_rows = []
    for iteration, group in boot_score_long.groupby("bootstrap"):
        wide = group.pivot(index="model_id", columns="dimension", values="score")
        synthetic = pd.DataFrame({"model_id": CORE_MODELS})
        for dim in q1.dimensions:
            code = dim_code(dim)
            synthetic[f"{dim}_score"] = synthetic["model_id"].map(wide[code])
        matrix = perspective_matrix(synthetic, q1.dimensions, perspective)
        weights = objective_weights(matrix, stability)
        ranking = rank_matrix(matrix, weights, q1, perspective)
        ranking["bootstrap"] = int(iteration)
        rank_rows.append(ranking[["bootstrap", "model_id", "overall_score", "rank"]])
        weights = weights.copy()
        weights["bootstrap"] = int(iteration)
        weight_rows.append(weights)
    return pd.concat(rank_rows, ignore_index=True), pd.concat(weight_rows, ignore_index=True)

def bootstrap_summary(boot: pd.DataFrame, main: pd.DataFrame, q1: Q1Data, perspective: str) -> pd.DataFrame:
    main_map = main.set_index("model_id")
    rows = []
    for model_id, group in boot.groupby("model_id"):
        rows.append(
            {
                "perspective": perspective,
                "model_id": model_id,
                "model": q1.model_names[model_id],
                "main_score": main_map.loc[model_id, "overall_score"],
                "main_rank": int(main_map.loc[model_id, "rank"]),
                "score_ci_low": group["overall_score"].quantile(0.025),
                "score_ci_high": group["overall_score"].quantile(0.975),
                "rank_ci_low": group["rank"].quantile(0.025),
                "rank_ci_high": group["rank"].quantile(0.975),
                "median_rank": group["rank"].median(),
                "top3_probability": float((group["rank"] <= 3).mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("main_rank")

def old_stability_audit(q1: Q1Data) -> pd.DataFrame:
    path = ROOT / "outputs" / "q1" / "bootstrap" / "bootstrap_dimension_scores_preliminary.csv"
    rows = []
    if path.exists():
        old = pd.read_csv(path)
        for dim in q1.dimensions:
            col = f"{dim}_score"
            sd = old.groupby("model_id")[col].std().dropna()
            vectors = old.pivot(index="bootstrap", columns="model_id", values=col).drop_duplicates()
            endpoint = old.groupby("model_id")[col].apply(lambda x: float(((x == 0) | (x == 100)).mean())).dropna()
            rows.append(
                {
                    "dimension": dim_code(dim),
                    "old_median_score_sd": float(sd.median()) if len(sd) else np.nan,
                    "old_unique_bootstrap_score_vectors": int(len(vectors)),
                    "old_median_endpoint_frequency": float(endpoint.median()) if len(endpoint) else np.nan,
                    "audit_conclusion": "PSEUDO_STABLE_RESAMPLING_DEGENERACY" if len(vectors) == 1 else "VARIATION_PRESENT",
                }
            )
    return pd.DataFrame(rows)

def family_screening_table(q1: Q1Data, corr: pd.DataFrame, common_n: pd.DataFrame, base_pairwise: pd.DataFrame) -> pd.DataFrame:
    manifest = q1.manifest.copy()
    registry = pd.read_csv(FROZEN_DIR / "source_registry_v1.0.csv")
    source_titles = registry.set_index("source_id")["source_title"].to_dict()
    baseline_active = {}
    for dim in q1.dimensions:
        baseline_active[dim_code(dim)] = set(
            base_pairwise.loc[base_pairwise["dimension"] == dim, ["model_i", "model_j"]].stack().unique()
        )
    rows = []
    for (dimension, family), group in manifest.groupby(["dimension", "benchmark_family"], sort=False):
        vals = corr.loc[family].drop(labels=[family], errors="ignore").abs().dropna()
        if len(vals):
            partner = vals.idxmax()
            max_abs = float(vals.loc[partner])
            n = int(common_n.loc[family, partner])
        else:
            partner, max_abs, n = "NONE", np.nan, 0
        removed = base_pairwise[base_pairwise["benchmark_family"] != family]
        dim_removed = removed[removed["dimension"] == dimension]
        graph = graph_diagnostics(dim_removed, CORE_MODELS)
        active_after = set(graph["active_models"])
        indispensable = active_after != baseline_active[dim_code(dimension)] or not graph["connected"]
        semantic = "; ".join(group["benchmark_name"].astype(str).drop_duplicates())
        sources = group["source"].astype(str).drop_duplicates().tolist()
        source_text = "; ".join(f"{s}: {source_titles.get(s, s)}" for s in sources)
        coverage = float(group["model_coverage"].astype(float).mean())
        if indispensable:
            decision = "KEEP_STRUCTURALLY_INDISPENSABLE"
            reason = "Removal changes the active comparison network or its connectivity."
        elif np.isfinite(max_abs) and max_abs >= 0.85:
            decision = "KEEP_REDUNDANCY_FLAG_SENSITIVITY_DELETE"
            reason = (
                "High correlation is not deletion proof; common_n is small or semantic/source roles differ."
                if n <= 3
                else "Retained for semantic/source independence and tested by LOFO."
            )
        else:
            decision = "KEEP_KEY_INDICATOR"
            reason = "Provides nonredundant semantic evidence with adequate network support."
        rows.append(
            {
                "dimension": dim_code(dimension),
                "benchmark_family": family,
                "model_coverage": coverage,
                "max_abs_spearman": max_abs,
                "most_correlated_family": partner,
                "common_n": n,
                "semantic_role": semantic,
                "network_role": "structurally indispensable" if indispensable else "supporting/redundant-tested",
                "source": source_text,
                "decision": decision,
                "reason": reason,
            }
        )
    return pd.DataFrame(rows)

def scenario_analysis(
    q1: Q1Data,
    main: dict[str, Any],
    ranking_a: pd.DataFrame,
    stability_a: dict[str, float],
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_active = {}
    for dim in q1.dimensions:
        pw = main["pairwise"][main["pairwise"]["dimension"] == dim]
        baseline_active[dim] = set(pw[["model_i", "model_j"]].stack().unique())
    if mode == "LOFO":
        scenarios = [(family, {"families": {family}}) for family in q1.families]
    else:
        scenarios = [
            ("LiveBench", {"source_ids": {"SRC006"}}),
            ("Artificial Analysis", {"source_ids": {"SRC014", "SRC016", "SRC017", "SRC018"}}),
            ("Kimi official/technical comparison", {"source_ids": {"SRC001"}}),
            ("DeepSeek technical report", {"source_ids": {"SRC003"}}),
            ("OpenRouter", {"source_ids": {"SRC007"}}),
        ]
    summary_rows, model_rows, dim_rows = [], [], []
    for scenario, spec in scenarios:
        long = q1.long.copy()
        if "families" in spec:
            long = long[~long["benchmark_family"].isin(spec["families"])].copy()
        else:
            long = long[~long["source_id"].isin(spec["source_ids"])].copy()
        result = fit_main(q1, long)
        valid = True
        for dim in q1.dimensions:
            pw = result["pairwise"][result["pairwise"]["dimension"] == dim]
            graph = graph_diagnostics(pw, CORE_MODELS)
            active = set(graph["active_models"])
            status = "OK"
            if active != baseline_active[dim] or not graph["connected"] or not result["diag"][dim]["converged"]:
                status = "NETWORK_DISCONNECTED"
                valid = False
            base_dim = main["scores"].set_index("model_id").get(f"{dim}_score")
            scenario_dim = result["scores"].set_index("model_id").get(f"{dim}_score")
            score_delta = np.nan
            if base_dim is not None and scenario_dim is not None:
                common = base_dim.index.intersection(scenario_dim.index)
                if len(common):
                    score_delta = float((scenario_dim.loc[common] - base_dim.loc[common]).abs().mean())
            dim_rows.append(
                {
                    "analysis": mode,
                    "removed": scenario,
                    "dimension": dim_code(dim),
                    "status": status,
                    "active_models": len(active),
                    "baseline_active_models": len(baseline_active[dim]),
                    "connected": graph["connected"],
                    "bt_converged": result["diag"][dim]["converged"],
                    "mean_abs_dimension_score_change": score_delta,
                }
            )
        if valid:
            matrix = perspective_matrix(result["scores"], q1.dimensions, "A")
            weights = objective_weights(matrix, stability_a)
            ranking = rank_matrix(matrix, weights, q1, "A")
            comp = rank_comparison(ranking_a, ranking, scenario)
            status = "OK"
            for row in ranking.itertuples(index=False):
                main_rank = int(ranking_a.loc[ranking_a["model_id"] == row.model_id, "rank"].iloc[0])
                model_rows.append(
                    {
                        "analysis": mode,
                        "removed": scenario,
                        "status": status,
                        "model_id": row.model_id,
                        "model": row.model,
                        "main_rank": main_rank,
                        "scenario_rank": int(row.rank),
                        "rank_change": int(row.rank) - main_rank,
                        "scenario_score": row.overall_score,
                    }
                )
            summary_rows.append({"analysis": mode, "removed": scenario, "status": status, **comp})
        else:
            summary_rows.append(
                {
                    "analysis": mode,
                    "removed": scenario,
                    "status": "NETWORK_DISCONNECTED",
                    "comparison": scenario,
                    "common_models": np.nan,
                    "spearman": np.nan,
                    "kendall_tau": np.nan,
                    "kimi_rank_A": int(ranking_a.loc[ranking_a["model_id"] == KIMI_MODEL_ID, "rank"].iloc[0]),
                    "kimi_rank_other": np.nan,
                    "top3_overlap_count": np.nan,
                    "top3_membership_A": "; ".join(ranking_a.nsmallest(3, "rank")["model_id"]),
                    "top3_membership_other": "NETWORK_DISCONNECTED",
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(model_rows), pd.DataFrame(dim_rows)

def equal_weight_table(
    q1: Q1Data,
    matrix: pd.DataFrame,
    objective_ranking: pd.DataFrame,
    perspective: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    equal = pd.DataFrame({"dimension": matrix.columns, "weight": [1.0 / len(matrix.columns)] * len(matrix.columns)})
    equal["information_I"] = np.nan
    equal["non_redundancy_R"] = np.nan
    equal["latent_rank_stability_T"] = np.nan
    equal["q"] = np.nan
    equal_rank = rank_matrix(matrix, equal, q1, f"{perspective}_EQUAL")
    merged = objective_ranking[["model_id", "model", "rank", "overall_score"]].merge(
        equal_rank[["model_id", "rank", "overall_score"]], on="model_id", suffixes=("_main", "_equal")
    )
    merged = merged.rename(
        columns={
            "rank_main": "main_rank",
            "rank_equal": "equal_weight_rank",
            "overall_score_main": "main_score",
            "overall_score_equal": "equal_weight_score",
        }
    )
    merged["rank_change"] = merged["equal_weight_rank"] - merged["main_rank"]
    merged["perspective"] = perspective
    comp = rank_comparison(objective_ranking, equal_rank, f"{perspective}: objective vs equal")
    return merged, comp
~~~~

## 5.3 Q2 KL-CES 数学模块

以下完整模块实现 KL、CES、缺失策略、边际分析、不确定性传播和敏感性计算。

### `src/q2/__init__.py`

~~~~python
"""Question 2: scenario-specific KL-CES utility evaluation.

This package is deliberately independent from ``src.q1``.  Q1 communicates
with Q2 only through the documented tabular interface in ``data/q2``.
"""

from .config import ABILITY_COLUMNS, EPS, SCENES
from .pipeline import Q2PipelineResult, build_q2_pipeline

__all__ = [
    "ABILITY_COLUMNS",
    "EPS",
    "SCENES",
    "Q2PipelineResult",
    "build_q2_pipeline",
]
~~~~

### `src/q2/ces.py`

~~~~python
"""Constant-elasticity-of-substitution (CES) scene utility."""

from __future__ import annotations

import numpy as np

from .config import EPS


RHO_ZERO_TOLERANCE = 1e-7


def _validate_inputs(values: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if z.shape[-1] != w.shape[0]:
        raise ValueError("The final ability axis must match the weight vector.")
    if np.isnan(z).any():
        raise ValueError("CES cannot silently consume missing abilities; apply a missing-data policy first.")
    if np.any(z < 0.0) or np.any(z > 1.0):
        raise ValueError("CES expects abilities normalised to [0, 1].")
    if np.any(w < 0.0) or not np.isclose(w.sum(), 1.0, atol=1e-10):
        raise ValueError("CES weights must be non-negative and sum to one.")
    return z, w


def ces_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Evaluate CES utility along the final axis.

    The rho=0 branch uses the continuous weighted-geometric-mean limit.
    """

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return np.exp(np.sum(w * np.log(x), axis=-1))
    inner = np.sum(w * np.power(x, float(rho)), axis=-1)
    return np.power(inner, 1.0 / float(rho))


def substitution_elasticity(rho: float) -> float:
    """Return sigma=1/(1-rho); rho=1 corresponds to infinite elasticity."""

    if np.isclose(rho, 1.0):
        return float("inf")
    return 1.0 / (1.0 - float(rho))
~~~~

### `src/q2/config.py`

~~~~python
"""Central configuration for the Q2 KL-CES model.

All numerical scenario assumptions live here.  The ranges are development
defaults for sensitivity analysis, not frozen competition conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass


ABILITY_COLUMNS = ("C1", "C2", "C3", "C4", "C5")
ABILITY_LABELS = {
    "C1": "复杂推理能力",
    "C2": "知识与事实可靠性",
    "C3": "长上下文处理能力",
    "C4": "代码与软件工程能力",
    "C5": "多模态能力",
}

EPS = 1e-6
BASE_WEIGHT_SOURCE = "Q1_FINAL"
Q1_FINALIZED = False
TENTATIVE_PARAMETER_RANGE = True
DEFAULT_ALPHA_GRID_SIZE = 9
DEFAULT_RHO_GRID_SIZE = 9
OPTIMIZER_TOLERANCE = 1e-10
CONSTRAINT_TOLERANCE = 1e-8


@dataclass(frozen=True)
class SceneConfig:
    """Parameterised demand system for one application scene."""

    key: str
    label: str
    core_dimensions: tuple[str, ...]
    alpha_range: tuple[float, float]
    alpha_development_default: float
    rho_range: tuple[float, float]
    rho_development_default: float
    lower_bounds: tuple[tuple[str, float], ...] = ()
    order_constraints: tuple[tuple[str, str], ...] = ()


SCENES: dict[str, SceneConfig] = {
    "research": SceneConfig(
        key="research",
        label="科研长文本分析",
        core_dimensions=("C3", "C1", "C2"),
        alpha_range=(0.55, 0.75),
        alpha_development_default=0.65,
        rho_range=(-0.60, 0.20),
        rho_development_default=-0.20,
        order_constraints=(("C3", "C4"), ("C1", "C5"), ("C2", "C4")),
    ),
    "dialogue": SceneConfig(
        key="dialogue",
        label="大众日常通用对话",
        core_dimensions=("C1", "C2", "C5"),
        alpha_range=(0.50, 0.70),
        alpha_development_default=0.60,
        rho_range=(0.10, 0.80),
        rho_development_default=0.45,
        lower_bounds=(("C2", 0.15),),
        order_constraints=(("C2", "C4"), ("C1", "C4"), ("C5", "C4")),
    ),
    "coding": SceneConfig(
        key="coding",
        label="计算机代码开发",
        core_dimensions=("C4", "C1"),
        alpha_range=(0.55, 0.75),
        alpha_development_default=0.65,
        rho_range=(-0.70, 0.20),
        rho_development_default=-0.25,
        lower_bounds=(("C4", 0.30),),
        order_constraints=(("C4", "C2"), ("C4", "C3"), ("C1", "C5")),
    ),
}


def equal_reference(dimensions: tuple[str, ...] = ABILITY_COLUMNS) -> dict[str, float]:
    """Return the equal-weight robustness prior on the requested dimensions."""

    if not dimensions:
        raise ValueError("At least one ability dimension is required.")
    value = 1.0 / len(dimensions)
    return {dimension: value for dimension in dimensions}
~~~~

### `src/q2/data_adapter.py`

~~~~python
"""Stable Q1-to-Q2 data contract and finalisation guard."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import ABILITY_COLUMNS


AVAILABILITY_COLUMNS = tuple(f"{dimension}_available" for dimension in ABILITY_COLUMNS)
REQUIRED_COLUMNS = ("model", *ABILITY_COLUMNS, *AVAILABILITY_COLUMNS)
OPTIONAL_COLUMNS = (
    "q1_overall_score",
    "q1_overall_rank",
    *(f"{dimension}_{bound}" for dimension in ABILITY_COLUMNS for bound in ("lower", "upper")),
)


@dataclass(frozen=True)
class Q1InputBundle:
    frame: pd.DataFrame
    metadata: dict[str, Any]
    objective_weights: dict[str, float] | None
    source_path: Path


def _coerce_bool(series: pd.Series, column: str) -> pd.Series:
    true_values = {True, 1, "1", "true", "t", "yes", "y"}
    false_values = {False, 0, "0", "false", "f", "no", "n"}

    def convert(value: Any) -> bool:
        if pd.isna(value):
            raise ValueError(f"Availability column {column!r} contains a missing flag.")
        normalised = value.strip().lower() if isinstance(value, str) else value
        if normalised in true_values:
            return True
        if normalised in false_values:
            return False
        raise ValueError(f"Invalid boolean value {value!r} in {column!r}.")

    return series.map(convert).astype(bool)


def _validate_metadata(metadata: dict[str, Any], mode: str) -> None:
    scale = metadata.get("ability_scale")
    if scale not in {"0-100", "0-1"}:
        raise ValueError("metadata.ability_scale must be either '0-100' or '0-1'.")
    normalised_mode = mode.upper()
    if normalised_mode not in {"DEVELOPMENT", "FINAL"}:
        raise ValueError("mode must be DEVELOPMENT or FINAL.")
    if normalised_mode == "FINAL":
        required = {
            "q1_finalized": metadata.get("q1_finalized") is True,
            "q1_freeze_version": bool(metadata.get("q1_freeze_version")),
            "q1_freeze_date": bool(metadata.get("q1_freeze_date")),
            "objective_weights_available": metadata.get("objective_weights_available") is True,
        }
        missing = [field for field, valid in required.items() if not valid]
        if missing:
            raise PermissionError(
                "FINAL mode is blocked until Q1 is frozen. Missing/invalid metadata: "
                + ", ".join(missing)
            )


def _read_objective_weights(metadata: dict[str, Any]) -> dict[str, float] | None:
    raw = metadata.get("objective_weights")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("metadata.objective_weights must be an object keyed by C1...C5.")
    missing = [dimension for dimension in ABILITY_COLUMNS if dimension not in raw]
    if missing:
        raise ValueError(f"Objective weights are missing: {missing}")
    weights = {dimension: float(raw[dimension]) for dimension in ABILITY_COLUMNS}
    values = np.asarray(list(weights.values()), dtype=float)
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("Objective weights must be finite and strictly positive for KL projection.")
    return {dimension: value / float(values.sum()) for dimension, value in weights.items()}


def load_q1_input(
    csv_path: str | Path,
    metadata_path: str | Path,
    mode: str = "DEVELOPMENT",
) -> Q1InputBundle:
    """Load and validate the standard Q1 output without importing Q1 code."""

    csv_file = Path(csv_path)
    metadata_file = Path(metadata_path)
    with metadata_file.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    _validate_metadata(metadata, mode)

    frame = pd.read_csv(csv_file)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Q1 input is missing required columns: {missing_columns}")
    if frame.empty:
        raise ValueError("Q1 input contains no model rows.")
    if frame["model"].isna().any() or frame["model"].astype(str).str.strip().eq("").any():
        raise ValueError("Every row must have a non-empty model name.")
    if frame["model"].duplicated().any():
        duplicated = frame.loc[frame["model"].duplicated(), "model"].tolist()
        raise ValueError(f"Model names must be unique; duplicates: {duplicated}")

    for column in AVAILABILITY_COLUMNS:
        frame[column] = _coerce_bool(frame[column], column)
    numeric_columns = [column for column in (*ABILITY_COLUMNS, *OPTIONAL_COLUMNS) if column in frame.columns]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    for dimension in ABILITY_COLUMNS:
        available = frame[f"{dimension}_available"]
        if frame.loc[available, dimension].isna().any():
            bad_models = frame.loc[available & frame[dimension].isna(), "model"].tolist()
            raise ValueError(
                f"{dimension} is marked available but missing for models: {bad_models}"
            )
        # An unavailable score is never allowed to leak into Q2 as an observed value.
        frame.loc[~available, dimension] = np.nan

    if mode.upper() == "DEVELOPMENT":
        if "MOCK_DATA_ONLY" not in frame.columns:
            raise PermissionError(
                "DEVELOPMENT inputs must contain MOCK_DATA_ONLY=TRUE to prevent use of Q1 half-products."
            )
        mock_flags = _coerce_bool(frame["MOCK_DATA_ONLY"], "MOCK_DATA_ONLY")
        if not bool(mock_flags.all()) or metadata.get("mock_data_only") is not True:
            raise PermissionError("Development execution is restricted to explicitly marked mock data.")
        frame["MOCK_DATA_ONLY"] = mock_flags

    objective_weights = _read_objective_weights(metadata)
    if mode.upper() == "FINAL" and objective_weights is None:
        raise PermissionError("FINAL mode requires Q1 objective weights.")
    return Q1InputBundle(frame=frame, metadata=metadata, objective_weights=objective_weights, source_path=csv_file)
~~~~

### `src/q2/imbalance_penalty.py`

~~~~python
"""Performance Imbalance Penalty Index (PRI)."""

from __future__ import annotations

import numpy as np


def imbalance_penalty(linear: np.ndarray, ces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return absolute penalty P=L-U and relative penalty PRI=(L-U)/L."""

    linear_values = np.asarray(linear, dtype=float)
    ces_values = np.asarray(ces, dtype=float)
    if linear_values.shape != ces_values.shape:
        raise ValueError("Linear and CES utility arrays must have the same shape.")
    penalty = linear_values - ces_values
    pri = np.divide(
        penalty,
        linear_values,
        out=np.full_like(penalty, np.nan, dtype=float),
        where=np.abs(linear_values) > 1e-15,
    )
    return penalty, pri
~~~~

### `src/q2/kl_weights.py`

~~~~python
"""Minimum-information-shift scenario weighting via KL projection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import xlogy

from .config import OPTIMIZER_TOLERANCE, SceneConfig
from .scene_constraints import (
    ActiveSceneConstraints,
    activate_constraints,
    constraint_diagnostics,
    find_feasible_weights,
    scipy_inequality_constraints,
)


@dataclass(frozen=True)
class KLWeightResult:
    scene: str
    dimensions: tuple[str, ...]
    weights: dict[str, float]
    prior: dict[str, float]
    alpha: float
    kl_divergence: float
    success: bool
    message: str
    diagnostics: dict[str, float | bool]


def _normalise_prior(prior: dict[str, float], dimensions: tuple[str, ...]) -> np.ndarray:
    try:
        values = np.asarray([prior[dimension] for dimension in dimensions], dtype=float)
    except KeyError as exc:
        raise ValueError(f"Prior is missing ability dimension {exc.args[0]!r}.") from exc
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("KL prior weights must be finite and strictly positive.")
    return values / values.sum()


def kl_divergence(weights: np.ndarray, prior: np.ndarray) -> float:
    """Compute D_KL(weights || prior), using the 0 log 0 convention."""

    w = np.asarray(weights, dtype=float)
    p = np.asarray(prior, dtype=float)
    return float(np.sum(xlogy(w, w / p)))


def solve_scene_weights(
    prior: dict[str, float],
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    alpha: float | None = None,
) -> KLWeightResult:
    """Project a neutral prior onto a scene's feasible demand set."""

    active: ActiveSceneConstraints = activate_constraints(scene, dimensions, alpha)
    p = _normalise_prior(prior, dimensions)
    feasible = find_feasible_weights(active)
    start = 0.5 * p + 0.5 * feasible
    constraints = [
        {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)},
        *scipy_inequality_constraints(active),
    ]
    result = minimize(
        fun=lambda w: kl_divergence(w, p),
        x0=start,
        method="SLSQP",
        bounds=[(0.0, 1.0) for _ in dimensions],
        constraints=constraints,
        options={"ftol": OPTIMIZER_TOLERANCE, "maxiter": 2000, "disp": False},
    )
    diagnostics = constraint_diagnostics(result.x, active)
    success = bool(result.success and diagnostics["feasible"])
    if not success:
        raise RuntimeError(
            f"KL projection failed for scene {scene.key}: {result.message}; "
            f"diagnostics={diagnostics}"
        )
    weights = {dimension: float(result.x[idx]) for idx, dimension in enumerate(dimensions)}
    prior_out = {dimension: float(p[idx]) for idx, dimension in enumerate(dimensions)}
    return KLWeightResult(
        scene=scene.key,
        dimensions=dimensions,
        weights=weights,
        prior=prior_out,
        alpha=active.alpha,
        kl_divergence=kl_divergence(result.x, p),
        success=success,
        message=str(result.message),
        diagnostics=diagnostics,
    )
~~~~

### `src/q2/linear_baseline.py`

~~~~python
"""Fully compensatory linear baseline used only for comparison."""

from __future__ import annotations

import numpy as np


def linear_utility(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    z = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if z.shape[-1] != w.shape[0]:
        raise ValueError("The final ability axis must match the weight vector.")
    if np.isnan(z).any():
        raise ValueError("Linear utility cannot silently consume missing abilities.")
    if np.any(w < 0.0) or not np.isclose(w.sum(), 1.0, atol=1e-10):
        raise ValueError("Weights must be non-negative and sum to one.")
    return np.sum(z * w, axis=-1)
~~~~

### `src/q2/marginal_analysis.py`

~~~~python
"""Nonlinear CES interpretation by inner shares and marginal utility."""

from __future__ import annotations

import numpy as np

from .ces import RHO_ZERO_TOLERANCE, _validate_inputs, ces_utility
from .config import EPS


def ces_inner_shares(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Return q_j = w_j x_j^rho / sum_k w_k x_k^rho."""

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return np.broadcast_to(w, z.shape).copy()
    numerator = w * np.power(x, float(rho))
    return numerator / np.sum(numerator, axis=-1, keepdims=True)


def ces_marginal_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Analytic derivative dU/dz_j for the CES aggregator."""

    z, w = _validate_inputs(values, weights)
    x = z + float(eps)
    utility = np.expand_dims(ces_utility(z, w, rho, eps), axis=-1)
    if abs(float(rho)) <= RHO_ZERO_TOLERANCE:
        return utility * w / x
    return w * np.power(x, float(rho) - 1.0) * np.power(utility, 1.0 - float(rho))


def ces_utility_elasticity(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    eps: float = EPS,
) -> np.ndarray:
    """Return E_j=(dU/dz_j)(z_j/U), using the unshifted normalised z_j."""

    z, w = _validate_inputs(values, weights)
    utility = np.expand_dims(ces_utility(z, w, rho, eps), axis=-1)
    marginal = ces_marginal_utility(z, w, rho, eps)
    return marginal * z / utility


def numerical_marginal_utility(
    values: np.ndarray,
    weights: np.ndarray,
    rho: float,
    step: float = 1e-6,
    eps: float = EPS,
) -> np.ndarray:
    """Central/one-sided finite differences for derivative verification."""

    z, w = _validate_inputs(values, weights)
    flat = np.atleast_2d(z).astype(float)
    derivatives = np.empty_like(flat)
    for row_idx, row in enumerate(flat):
        for col_idx in range(row.size):
            lower = row.copy()
            upper = row.copy()
            lower[col_idx] = max(0.0, lower[col_idx] - step)
            upper[col_idx] = min(1.0, upper[col_idx] + step)
            width = upper[col_idx] - lower[col_idx]
            derivatives[row_idx, col_idx] = (
                float(ces_utility(upper, w, rho, eps))
                - float(ces_utility(lower, w, rho, eps))
            ) / width
    return derivatives[0] if z.ndim == 1 else derivatives
~~~~

### `src/q2/missing_policy.py`

~~~~python
"""Explicit missing-ability policies; no implicit zero filling is permitted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import ABILITY_COLUMNS, EPS


@dataclass(frozen=True)
class MissingPolicyResult:
    frame: pd.DataFrame
    dimensions: tuple[str, ...]
    label: str
    excluded_models: tuple[str, ...] = ()


def apply_missing_policy(
    frame: pd.DataFrame,
    mode: str,
    dimensions: tuple[str, ...] = ABILITY_COLUMNS,
    metadata: dict[str, Any] | None = None,
) -> MissingPolicyResult:
    """Apply complete-case, common-dimension, or inherited Q1 policy."""

    normalised_mode = mode.lower()
    if normalised_mode == "complete_case":
        mask = frame[list(dimensions)].notna().all(axis=1)
        excluded = tuple(frame.loc[~mask, "model"].astype(str))
        return MissingPolicyResult(
            frame=frame.loc[mask].copy().reset_index(drop=True),
            dimensions=dimensions,
            label="COMPLETE_CASE_RESULT",
            excluded_models=excluded,
        )
    if normalised_mode == "common_dimension":
        common = tuple(dimension for dimension in dimensions if frame[dimension].notna().all())
        if not common:
            raise ValueError("No ability dimension is jointly observed by all participating models.")
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=common,
            label="COMMON_DIMENSION_RESULT",
        )
    if normalised_mode == "q1_final_policy":
        metadata = metadata or {}
        if metadata.get("q1_missing_policy_applied") is not True:
            raise PermissionError(
                "q1_final_policy requires metadata.q1_missing_policy_applied=true."
            )
        if frame[list(dimensions)].isna().any().any():
            raise ValueError("Q1 final policy is declared, but the inherited ability matrix still contains NA.")
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=dimensions,
            label="Q1_FINAL_POLICY_RESULT",
        )
    if normalised_mode == "interval_propagation":
        return MissingPolicyResult(
            frame=frame.copy().reset_index(drop=True),
            dimensions=dimensions,
            label="INTERVAL_PROPAGATION_RESULT",
        )
    raise ValueError(
        "Unknown missing policy. Choose complete_case, common_dimension, "
        "interval_propagation, or q1_final_policy."
    )


def utility_intervals(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
    eps: float = EPS,
) -> pd.DataFrame:
    """Propagate monotone ability intervals through CES and bound possible ranks."""

    lower_rows: list[list[float]] = []
    upper_rows: list[list[float]] = []
    for _, row in frame.iterrows():
        lower_values: list[float] = []
        upper_values: list[float] = []
        for dimension in dimensions:
            value = row.get(dimension)
            lower = row.get(f"{dimension}_lower", np.nan)
            upper = row.get(f"{dimension}_upper", np.nan)
            if pd.notna(value):
                lower = value if pd.isna(lower) else lower
                upper = value if pd.isna(upper) else upper
            if pd.isna(lower) or pd.isna(upper):
                raise ValueError(
                    f"Model {row['model']!r} needs {dimension}_lower and {dimension}_upper "
                    "for interval propagation."
                )
            lower_float, upper_float = float(lower), float(upper)
            if not 0.0 <= lower_float <= upper_float <= 1.0:
                raise ValueError(f"Invalid interval [{lower_float}, {upper_float}] for {dimension}.")
            lower_values.append(lower_float)
            upper_values.append(upper_float)
        lower_rows.append(lower_values)
        upper_rows.append(upper_values)

    weight_vector = np.asarray([weights[d] for d in dimensions], dtype=float)
    lower_utility = np.asarray(ces_utility(np.asarray(lower_rows), weight_vector, rho, eps))
    upper_utility = np.asarray(ces_utility(np.asarray(upper_rows), weight_vector, rho, eps))
    output = pd.DataFrame(
        {
            "model": frame["model"].astype(str).to_numpy(),
            "utility_lower": lower_utility,
            "utility_upper": upper_utility,
        }
    )
    best_ranks: list[int] = []
    worst_ranks: list[int] = []
    for idx in range(len(output)):
        best_ranks.append(1 + int(np.sum(np.delete(lower_utility, idx) > upper_utility[idx])))
        worst_ranks.append(1 + int(np.sum(np.delete(upper_utility, idx) > lower_utility[idx])))
    output["best_possible_rank"] = best_ranks
    output["worst_possible_rank"] = worst_ranks
    return output
~~~~

### `src/q2/normalize.py`

~~~~python
"""Ability scaling for Q2, preserving missing values exactly."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ABILITY_COLUMNS


def normalise_abilities(
    frame: pd.DataFrame,
    ability_scale: str,
    dimensions: tuple[str, ...] = ABILITY_COLUMNS,
) -> pd.DataFrame:
    """Return a copy with ability scores on [0,1]; NaN remains NaN."""

    if ability_scale not in {"0-100", "0-1"}:
        raise ValueError("ability_scale must be '0-100' or '0-1'.")
    result = frame.copy()
    factor = 100.0 if ability_scale == "0-100" else 1.0
    for dimension in dimensions:
        numeric = pd.to_numeric(result[dimension], errors="coerce")
        observed = numeric.dropna()
        upper = 100.0 if ability_scale == "0-100" else 1.0
        if ((observed < 0.0) | (observed > upper)).any():
            raise ValueError(f"{dimension} contains values outside the declared {ability_scale} scale.")
        result[dimension] = numeric / factor
        for bound in ("lower", "upper"):
            column = f"{dimension}_{bound}"
            if column in result.columns:
                interval = pd.to_numeric(result[column], errors="coerce")
                observed_interval = interval.dropna()
                if ((observed_interval < 0.0) | (observed_interval > upper)).any():
                    raise ValueError(f"{column} lies outside the declared {ability_scale} scale.")
                result[column] = interval / factor
    return result
~~~~

### `src/q2/pairwise_analysis.py`

~~~~python
"""Mechanism-oriented model comparison and target-model analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .imbalance_penalty import imbalance_penalty
from .linear_baseline import linear_utility
from .marginal_analysis import ces_inner_shares, ces_marginal_utility
from .rank_migration import identify_competitors


def compare_models(
    frame: pd.DataFrame,
    model_a: str,
    model_b: str,
    scene: str,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
) -> dict[str, Any]:
    """Explain a pairwise scene-utility gap without treating w_j z_j as CES contribution."""

    indexed = frame.set_index("model")
    missing = [model for model in (model_a, model_b) if model not in indexed.index]
    if missing:
        raise KeyError(f"Models absent from comparison frame: {missing}")
    z_a = indexed.loc[model_a, list(dimensions)].to_numpy(dtype=float)
    z_b = indexed.loc[model_b, list(dimensions)].to_numpy(dtype=float)
    w = np.asarray([weights[d] for d in dimensions], dtype=float)
    u_a, u_b = float(ces_utility(z_a, w, rho)), float(ces_utility(z_b, w, rho))
    l_a, l_b = float(linear_utility(z_a, w)), float(linear_utility(z_b, w))
    _, pri_a = imbalance_penalty(np.asarray([l_a]), np.asarray([u_a]))
    _, pri_b = imbalance_penalty(np.asarray([l_b]), np.asarray([u_b]))
    shares_a = ces_inner_shares(z_a, w, rho)
    shares_b = ces_inner_shares(z_b, w, rho)
    marginal_a = ces_marginal_utility(z_a, w, rho)
    marginal_b = ces_marginal_utility(z_b, w, rho)
    ability_gap = z_a - z_b
    weighted_effect = w * ability_gap
    return {
        "scene": scene,
        "model_a": model_a,
        "model_b": model_b,
        "utility_a": u_a,
        "utility_b": u_b,
        "utility_gap_a_minus_b": u_a - u_b,
        "linear_gap_a_minus_b": l_a - l_b,
        "ces_curvature_gap_effect": (u_a - u_b) - (l_a - l_b),
        "ability_difference": dict(zip(dimensions, ability_gap.tolist())),
        "weighted_ability_effect": dict(zip(dimensions, weighted_effect.tolist())),
        "ces_inner_share_a": dict(zip(dimensions, shares_a.tolist())),
        "ces_inner_share_b": dict(zip(dimensions, shares_b.tolist())),
        "marginal_utility_a": dict(zip(dimensions, marginal_a.tolist())),
        "marginal_utility_b": dict(zip(dimensions, marginal_b.tolist())),
        "priority_improvement_a": dimensions[int(np.argmax(marginal_a))],
        "priority_improvement_b": dimensions[int(np.argmax(marginal_b))],
        "pri_a": float(pri_a[0]),
        "pri_b": float(pri_b[0]),
        "larger_shortfall_penalty": model_a if pri_a[0] > pri_b[0] else model_b,
    }


def analyze_target_model(
    ability_frame: pd.DataFrame,
    scene_results: dict[str, pd.DataFrame],
    scene_weights: dict[str, dict[str, float]],
    scene_rho: dict[str, float],
    scene_dimensions: dict[str, tuple[str, ...]],
    model_name: str = "Kimi K3",
    rank_migration: pd.DataFrame | None = None,
    sensitivity_summary: dict[str, pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Assemble a result-driven target report after final data become available."""

    report: dict[str, Any] = {"model": model_name, "scenes": {}}
    for scene, result in scene_results.items():
        row = result.loc[result["model"] == model_name]
        if row.empty:
            report["scenes"][scene] = {"available": False}
            continue
        record = row.iloc[0]
        dimensions = scene_dimensions[scene]
        competitors = identify_competitors(result, model_name)
        comparisons = {}
        for role, competitor in competitors.items():
            if competitor is not None and competitor != model_name:
                comparisons[role] = compare_models(
                    ability_frame,
                    model_name,
                    competitor,
                    scene,
                    dimensions,
                    scene_weights[scene],
                    scene_rho[scene],
                )
        report["scenes"][scene] = {
            "available": True,
            "rank": int(record["rank"]),
            "utility": float(record["utility"]),
            "pri": float(record["pri"]),
            "rho": float(scene_rho[scene]),
            "ces_inner_shares": {
                dimension: float(record[f"inner_share_{dimension}"])
                for dimension in dimensions
            },
            "marginal_utilities": {
                dimension: float(record[f"marginal_utility_{dimension}"])
                for dimension in dimensions
            },
            "utility_elasticities": {
                dimension: float(record[f"elasticity_{dimension}"])
                for dimension in dimensions
            },
            "priority_improvement": max(
                dimensions,
                key=lambda dimension: float(record[f"marginal_utility_{dimension}"]),
            ),
            "competitors": competitors,
            "comparisons": comparisons,
        }
        if sensitivity_summary and scene in sensitivity_summary:
            summary_row = sensitivity_summary[scene]
            summary_row = summary_row[summary_row["model"] == target_model]
            if not summary_row.empty:
                report["scenes"][scene]["sensitivity"] = summary_row.iloc[0].to_dict()
    if rank_migration is not None:
        migration = rank_migration[rank_migration["model"] == model_name]
        report["rank_migration"] = None if migration.empty else migration.iloc[0].to_dict()
    return report
~~~~

### `src/q2/pipeline.py`

~~~~python
"""Composable, guarded Q2 pipeline; intentionally not an executable script."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import ABILITY_COLUMNS, SCENES, equal_reference
from .data_adapter import Q1InputBundle, load_q1_input
from .imbalance_penalty import imbalance_penalty
from .kl_weights import KLWeightResult, solve_scene_weights
from .linear_baseline import linear_utility
from .marginal_analysis import (
    ces_inner_shares,
    ces_marginal_utility,
    ces_utility_elasticity,
)
from .missing_policy import MissingPolicyResult, apply_missing_policy, utility_intervals
from .normalize import normalise_abilities
from .rank_migration import build_rank_migration


@dataclass(frozen=True)
class Q2PipelineResult:
    mode: str
    metadata: dict[str, Any]
    missing_policy: str
    result_label: str
    ability_frame: pd.DataFrame
    scene_results: dict[str, pd.DataFrame]
    interval_results: dict[str, pd.DataFrame]
    weight_results: dict[str, KLWeightResult]
    scene_dimensions: dict[str, tuple[str, ...]]
    scene_rho: dict[str, float]
    rank_migration: pd.DataFrame | None


def _select_prior(bundle: Q1InputBundle, prior_kind: str) -> dict[str, float]:
    kind = prior_kind.lower()
    if kind == "q1":
        if bundle.objective_weights is None:
            raise ValueError("The Q1 prior was requested, but objective_weights are unavailable.")
        return bundle.objective_weights
    if kind == "equal":
        return equal_reference()
    raise ValueError("prior_kind must be 'q1' or 'equal'.")


def _scene_result(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    weights: dict[str, float],
    rho: float,
    scene: str,
    result_label: str,
) -> pd.DataFrame:
    values = frame[list(dimensions)].to_numpy(dtype=float)
    weight_vector = np.asarray([weights[d] for d in dimensions], dtype=float)
    utility = np.asarray(ces_utility(values, weight_vector, rho), dtype=float)
    linear = np.asarray(linear_utility(values, weight_vector), dtype=float)
    penalty, pri = imbalance_penalty(linear, utility)
    shares = ces_inner_shares(values, weight_vector, rho)
    marginal = ces_marginal_utility(values, weight_vector, rho)
    elasticity = ces_utility_elasticity(values, weight_vector, rho)
    output = pd.DataFrame(
        {
            "model": frame["model"].astype(str).to_numpy(),
            "scene": scene,
            "utility": utility,
            "linear_utility": linear,
            "imbalance_penalty": penalty,
            "pri": pri,
            "rho": float(rho),
            "result_label": result_label,
        }
    )
    output["rank"] = output["utility"].rank(method="min", ascending=False).astype(int)
    output["linear_rank"] = output["linear_utility"].rank(method="min", ascending=False).astype(int)
    output["rank_ces_minus_linear"] = output["rank"] - output["linear_rank"]
    for idx, dimension in enumerate(dimensions):
        output[f"inner_share_{dimension}"] = shares[:, idx]
        output[f"marginal_utility_{dimension}"] = marginal[:, idx]
        output[f"elasticity_{dimension}"] = elasticity[:, idx]
    return output.sort_values(["rank", "model"]).reset_index(drop=True)


def build_q2_pipeline(
    csv_path: str | Path,
    metadata_path: str | Path,
    *,
    mode: str = "DEVELOPMENT",
    missing_mode: str = "complete_case",
    prior_kind: str = "q1",
    alpha_overrides: dict[str, float] | None = None,
    rho_overrides: dict[str, float] | None = None,
) -> Q2PipelineResult:
    """Build scene results in memory after enforcing the Q1-freeze guard.

    No files are written.  Development mode accepts only explicitly marked
    anonymous mock data; final mode requires frozen Q1 metadata.
    """

    normalised_mode = mode.upper()
    bundle = load_q1_input(csv_path, metadata_path, normalised_mode)
    frame = normalise_abilities(bundle.frame, bundle.metadata["ability_scale"])
    policy: MissingPolicyResult = apply_missing_policy(
        frame, missing_mode, ABILITY_COLUMNS, bundle.metadata
    )
    prior = _select_prior(bundle, prior_kind)
    alpha_overrides = alpha_overrides or {}
    rho_overrides = rho_overrides or {}

    scene_results: dict[str, pd.DataFrame] = {}
    interval_results: dict[str, pd.DataFrame] = {}
    weight_results: dict[str, KLWeightResult] = {}
    scene_dimensions: dict[str, tuple[str, ...]] = {}
    scene_rho: dict[str, float] = {}
    for scene_key, scene in SCENES.items():
        dimensions = policy.dimensions
        alpha = alpha_overrides.get(scene_key, scene.alpha_development_default)
        rho = float(rho_overrides.get(scene_key, scene.rho_development_default))
        weight_result = solve_scene_weights(prior, scene, dimensions, alpha)
        weight_results[scene_key] = weight_result
        scene_dimensions[scene_key] = dimensions
        scene_rho[scene_key] = rho
        if missing_mode.lower() == "interval_propagation":
            interval = utility_intervals(
                policy.frame, dimensions, weight_result.weights, rho
            )
            interval["scene"] = scene_key
            interval["rho"] = rho
            interval["result_label"] = policy.label
            interval_results[scene_key] = interval
        else:
            scene_results[scene_key] = _scene_result(
                policy.frame,
                dimensions,
                weight_result.weights,
                rho,
                scene_key,
                policy.label,
            )

    migration = None
    if scene_results:
        q1_frame = policy.frame if "q1_overall_rank" in policy.frame.columns else None
        migration = build_rank_migration(scene_results, q1_frame)
    return Q2PipelineResult(
        mode=normalised_mode,
        metadata=bundle.metadata,
        missing_policy=missing_mode,
        result_label=policy.label,
        ability_frame=policy.frame,
        scene_results=scene_results,
        interval_results=interval_results,
        weight_results=weight_results,
        scene_dimensions=scene_dimensions,
        scene_rho=scene_rho,
        rank_migration=migration,
    )


def write_pipeline_tables(result: Q2PipelineResult, output_directory: str | Path) -> list[Path]:
    """Write tables only to the mode-appropriate protected Q2 directory."""

    output = Path(output_directory).resolve()
    normalised = str(output).replace("\\", "/").lower()
    if result.mode == "DEVELOPMENT":
        if "/outputs/q2/dev" not in normalised:
            raise PermissionError("Development results may only be written under outputs/q2/dev.")
        prefix = "MOCK_DATA_ONLY__"
    elif result.mode == "FINAL":
        if result.metadata.get("q1_finalized") is not True:
            raise PermissionError("Final output is blocked because Q1 is not finalized.")
        if "/outputs/q2/final" not in normalised:
            raise PermissionError("Final results may only be written under outputs/q2/final.")
        prefix = ""
    else:
        raise ValueError(f"Unsupported result mode {result.mode!r}.")

    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for scene, table in result.scene_results.items():
        path = output / f"{prefix}{scene}_results.csv"
        table.to_csv(path, index=False)
        written.append(path)
    for scene, table in result.interval_results.items():
        path = output / f"{prefix}{scene}_interval_results.csv"
        table.to_csv(path, index=False)
        written.append(path)
    if result.rank_migration is not None:
        path = output / f"{prefix}rank_migration.csv"
        result.rank_migration.to_csv(path, index=False)
        written.append(path)
    return written
~~~~

### `src/q2/rank_migration.py`

~~~~python
"""Rank calculation and cross-scene migration tables."""

from __future__ import annotations

import pandas as pd


def rank_utilities(frame: pd.DataFrame, utility_column: str = "utility") -> pd.DataFrame:
    result = frame.copy()
    result["rank"] = result[utility_column].rank(method="min", ascending=False).astype(int)
    return result.sort_values(["rank", "model"]).reset_index(drop=True)


def build_rank_migration(
    scene_results: dict[str, pd.DataFrame],
    q1_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build wide ranks and Delta R=R_scene-R_Q1 when a Q1 rank exists."""

    tables: list[pd.DataFrame] = []
    if q1_frame is not None and "q1_overall_rank" in q1_frame.columns:
        baseline = q1_frame[["model", "q1_overall_rank"]].dropna().copy()
        baseline = baseline.rename(columns={"q1_overall_rank": "rank_q1"})
        tables.append(baseline)
    for scene, result in scene_results.items():
        if "rank" not in result.columns:
            result = rank_utilities(result)
        tables.append(result[["model", "rank"]].rename(columns={"rank": f"rank_{scene}"}))
    if not tables:
        raise ValueError("At least one rank table is required.")
    migration = tables[0]
    for table in tables[1:]:
        migration = migration.merge(table, on="model", how="outer", validate="one_to_one")
    if "rank_q1" in migration.columns:
        for scene in scene_results:
            column = f"rank_{scene}"
            migration[f"delta_rank_{scene}"] = migration[column] - migration["rank_q1"]
    return migration.sort_values("model").reset_index(drop=True)


def identify_competitors(scene_result: pd.DataFrame, target_model: str) -> dict[str, str | None]:
    """Identify adjacent, first-place, and nearest-utility competitors automatically."""

    ranked = rank_utilities(scene_result) if "rank" not in scene_result.columns else scene_result.copy()
    ranked = ranked.sort_values(["rank", "model"]).reset_index(drop=True)
    matches = ranked.index[ranked["model"] == target_model].tolist()
    if not matches:
        raise KeyError(f"Target model {target_model!r} is absent from the scene result.")
    idx = matches[0]
    target_utility = float(ranked.loc[idx, "utility"])
    others = ranked[ranked["model"] != target_model].copy()
    if others.empty:
        closest = None
    else:
        closest = str(
            others.loc[(others["utility"] - target_utility).abs().idxmin(), "model"]
        )
    return {
        "previous_rank": str(ranked.loc[idx - 1, "model"]) if idx > 0 else None,
        "next_rank": str(ranked.loc[idx + 1, "model"]) if idx + 1 < len(ranked) else None,
        "scene_first": str(ranked.iloc[0]["model"]),
        "closest_utility": closest,
    }
~~~~

### `src/q2/scene_constraints.py`

~~~~python
"""Construction and validation of parameterised scene constraints."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from .config import CONSTRAINT_TOLERANCE, SceneConfig


@dataclass(frozen=True)
class ActiveSceneConstraints:
    scene: str
    dimensions: tuple[str, ...]
    alpha: float
    core_dimensions: tuple[str, ...]
    lower_bounds: tuple[tuple[str, float], ...]
    order_constraints: tuple[tuple[str, str], ...]


def activate_constraints(
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    alpha: float | None = None,
) -> ActiveSceneConstraints:
    """Restrict a scene demand system to currently available dimensions.

    This is essential for ``common_dimension`` analysis.  Constraints that
    reference an unavailable dimension are removed, while the core-mass
    threshold remains attached to the surviving core dimensions.
    """

    if len(set(dimensions)) != len(dimensions):
        raise ValueError("Ability dimensions must be unique.")
    chosen_alpha = scene.alpha_development_default if alpha is None else float(alpha)
    if not 0.0 <= chosen_alpha <= 1.0:
        raise ValueError("alpha must lie in [0, 1].")
    core = tuple(d for d in scene.core_dimensions if d in dimensions)
    if not core:
        raise ValueError(f"Scene {scene.key!r} has no core dimension in the active data.")
    lower = tuple((d, value) for d, value in scene.lower_bounds if d in dimensions)
    orders = tuple(
        (higher, lower_dim)
        for higher, lower_dim in scene.order_constraints
        if higher in dimensions and lower_dim in dimensions
    )
    return ActiveSceneConstraints(
        scene=scene.key,
        dimensions=dimensions,
        alpha=chosen_alpha,
        core_dimensions=core,
        lower_bounds=lower,
        order_constraints=orders,
    )


def scipy_inequality_constraints(active: ActiveSceneConstraints) -> list[dict]:
    """Translate the active system to SLSQP constraints ``fun(w) >= 0``."""

    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    constraints: list[dict] = []
    core_idx = np.array([index[d] for d in active.core_dimensions], dtype=int)
    constraints.append(
        {"type": "ineq", "fun": lambda w, idx=core_idx, a=active.alpha: float(np.sum(w[idx]) - a)}
    )
    for dimension, lower in active.lower_bounds:
        idx = index[dimension]
        constraints.append(
            {"type": "ineq", "fun": lambda w, i=idx, bound=lower: float(w[i] - bound)}
        )
    for higher, lower_dim in active.order_constraints:
        high_idx, low_idx = index[higher], index[lower_dim]
        constraints.append(
            {"type": "ineq", "fun": lambda w, hi=high_idx, lo=low_idx: float(w[hi] - w[lo])}
        )
    return constraints


def find_feasible_weights(active: ActiveSceneConstraints) -> np.ndarray:
    """Find a feasible simplex point with linear programming."""

    n = len(active.dimensions)
    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []

    core_row = np.zeros(n)
    for dimension in active.core_dimensions:
        core_row[index[dimension]] = -1.0
    a_ub.append(core_row)
    b_ub.append(-active.alpha)

    for higher, lower_dim in active.order_constraints:
        row = np.zeros(n)
        row[index[higher]] = -1.0
        row[index[lower_dim]] = 1.0
        a_ub.append(row)
        b_ub.append(0.0)

    bounds = [(0.0, 1.0) for _ in range(n)]
    for dimension, lower in active.lower_bounds:
        bounds[index[dimension]] = (lower, 1.0)

    result = linprog(
        c=np.zeros(n),
        A_ub=np.vstack(a_ub),
        b_ub=np.asarray(b_ub),
        A_eq=np.ones((1, n)),
        b_eq=np.ones(1),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        raise ValueError(f"Infeasible constraints for scene {active.scene}: {result.message}")
    return np.asarray(result.x, dtype=float)


def constraint_diagnostics(
    weights: np.ndarray,
    active: ActiveSceneConstraints,
    tolerance: float = CONSTRAINT_TOLERANCE,
) -> dict[str, float | bool]:
    """Report simplex and scene-demand residuals."""

    values = np.asarray(weights, dtype=float)
    index = {dimension: idx for idx, dimension in enumerate(active.dimensions)}
    diagnostics: dict[str, float | bool] = {
        "weight_sum": float(values.sum()),
        "minimum_weight": float(values.min()),
        "core_mass": float(sum(values[index[d]] for d in active.core_dimensions)),
    }
    residuals = [diagnostics["core_mass"] - active.alpha]
    for dimension, lower in active.lower_bounds:
        residuals.append(float(values[index[dimension]] - lower))
    for higher, lower_dim in active.order_constraints:
        residuals.append(float(values[index[higher]] - values[index[lower_dim]]))
    diagnostics["minimum_constraint_residual"] = float(min(residuals))
    diagnostics["feasible"] = bool(
        abs(float(values.sum()) - 1.0) <= tolerance
        and float(values.min()) >= -tolerance
        and min(residuals) >= -tolerance
    )
    return diagnostics
~~~~

### `src/q2/sensitivity.py`

~~~~python
"""One- and two-dimensional alpha/rho robustness analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .ces import ces_utility
from .config import DEFAULT_ALPHA_GRID_SIZE, DEFAULT_RHO_GRID_SIZE, SceneConfig
from .kl_weights import solve_scene_weights


def parameter_grid(
    scene: SceneConfig,
    alpha_values: np.ndarray | None = None,
    rho_values: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    alpha = (
        np.linspace(*scene.alpha_range, DEFAULT_ALPHA_GRID_SIZE)
        if alpha_values is None
        else np.asarray(alpha_values, dtype=float)
    )
    rho = (
        np.linspace(*scene.rho_range, DEFAULT_RHO_GRID_SIZE)
        if rho_values is None
        else np.asarray(rho_values, dtype=float)
    )
    return alpha, rho


def run_sensitivity_grid(
    frame: pd.DataFrame,
    scene: SceneConfig,
    dimensions: tuple[str, ...],
    prior: dict[str, float],
    alpha_values: np.ndarray | None = None,
    rho_values: np.ndarray | None = None,
) -> pd.DataFrame:
    """Evaluate Rank_i=f(alpha,rho) over a rectangular parameter grid."""

    alpha_grid, rho_grid = parameter_grid(scene, alpha_values, rho_values)
    values = frame[list(dimensions)].to_numpy(dtype=float)
    if np.isnan(values).any():
        raise ValueError("Sensitivity analysis requires an explicit missing-data policy first.")
    records: list[pd.DataFrame] = []
    for alpha in alpha_grid:
        weight_result = solve_scene_weights(prior, scene, dimensions, float(alpha))
        weights = np.asarray([weight_result.weights[d] for d in dimensions], dtype=float)
        for rho in rho_grid:
            utility = ces_utility(values, weights, float(rho))
            block = pd.DataFrame(
                {
                    "model": frame["model"].astype(str).to_numpy(),
                    "scene": scene.key,
                    "alpha": float(alpha),
                    "rho": float(rho),
                    "utility": utility,
                    "kl_divergence": weight_result.kl_divergence,
                }
            )
            block["rank"] = block["utility"].rank(method="min", ascending=False).astype(int)
            block["top3"] = block["rank"] <= 3
            records.append(block)
    return pd.concat(records, ignore_index=True)


def summarise_rank_robustness(grid: pd.DataFrame) -> pd.DataFrame:
    """Summarise average/best/worst rank, Top-3 share, variability and jumps."""

    required = {"model", "alpha", "rho", "rank", "top3"}
    if not required.issubset(grid.columns):
        raise ValueError(f"Sensitivity grid is missing columns: {sorted(required - set(grid.columns))}")
    ordered = grid.sort_values(["model", "rho", "alpha"])
    jump = ordered.groupby(["model", "rho"])["rank"].diff().abs().fillna(0)
    ordered = ordered.assign(rank_jump=jump)
    summary = (
        ordered.groupby("model", as_index=False)
        .agg(
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
            top3_share=("top3", "mean"),
            rank_std=("rank", "std"),
            maximum_adjacent_alpha_jump=("rank_jump", "max"),
        )
        .fillna({"rank_std": 0.0})
    )
    summary["has_rank_jump"] = summary["maximum_adjacent_alpha_jump"] > 0
    return summary.sort_values(["mean_rank", "model"]).reset_index(drop=True)


def detect_rank_jump_thresholds(grid: pd.DataFrame) -> pd.DataFrame:
    """Locate adjacent-alpha intervals where a model's rank changes at fixed rho."""

    required = {"model", "scene", "alpha", "rho", "rank"}
    if not required.issubset(grid.columns):
        raise ValueError(f"Sensitivity grid is missing columns: {sorted(required - set(grid.columns))}")
    records: list[dict[str, float | int | str]] = []
    ordered = grid.sort_values(["model", "rho", "alpha"])
    for (model, rho), group in ordered.groupby(["model", "rho"], sort=False):
        previous = None
        for row in group.itertuples(index=False):
            if previous is not None and int(row.rank) != int(previous.rank):
                records.append(
                    {
                        "model": str(model),
                        "scene": str(row.scene),
                        "rho": float(rho),
                        "alpha_from": float(previous.alpha),
                        "alpha_to": float(row.alpha),
                        "rank_from": int(previous.rank),
                        "rank_to": int(row.rank),
                        "rank_jump": int(row.rank) - int(previous.rank),
                    }
                )
            previous = row
    return pd.DataFrame(
        records,
        columns=[
            "model",
            "scene",
            "rho",
            "alpha_from",
            "alpha_to",
            "rank_from",
            "rank_to",
            "rank_jump",
        ],
    )


def compare_prior_robustness(
    q1_prior_grid: pd.DataFrame,
    equal_prior_grid: pd.DataFrame,
) -> pd.DataFrame:
    """Compare rank distributions under Q1-objective and equal reference priors."""

    q1_summary = summarise_rank_robustness(q1_prior_grid).add_suffix("_q1_prior")
    q1_summary = q1_summary.rename(columns={"model_q1_prior": "model"})
    equal_summary = summarise_rank_robustness(equal_prior_grid).add_suffix("_equal_prior")
    equal_summary = equal_summary.rename(columns={"model_equal_prior": "model"})
    comparison = q1_summary.merge(equal_summary, on="model", validate="one_to_one")
    comparison["mean_rank_prior_shift"] = (
        comparison["mean_rank_equal_prior"] - comparison["mean_rank_q1_prior"]
    )
    comparison["top3_share_prior_shift"] = (
        comparison["top3_share_equal_prior"] - comparison["top3_share_q1_prior"]
    )
    return comparison.sort_values(["mean_rank_q1_prior", "model"]).reset_index(drop=True)


def rank_surface(grid: pd.DataFrame, model: str) -> pd.DataFrame:
    """Return a rho-by-alpha rank surface suitable for heatmap plotting."""

    subset = grid[grid["model"] == model]
    if subset.empty:
        raise KeyError(f"Model {model!r} is absent from the sensitivity grid.")
    return subset.pivot(index="rho", columns="alpha", values="rank").sort_index(ascending=False)
~~~~

### `q2/model_spec_v1.yaml`

~~~~yaml
model_spec_version: "q2-kl-ces-v1.0"
MODEL_SPEC_FROZEN_BEFORE_RESULTS: true
frozen_at_local_date: "2026-08-17"
specification_principle: >-
  Scene definitions, alpha/rho regions, transformations, and missingness rules
  are fixed from task semantics and Q1 metadata before any Q2 scene ranking is computed.

abilities:
  C1: "复杂推理"
  C2: "知识与事实可靠性"
  C3: "长上下文"
  C4: "代码与软件工程"
  C5: "多模态"

scenes:
  research:
    label: "科研长文本分析"
    ces_core_dimensions: [C1, C2, C3]
    kl_focus_dimensions: [C1, C3]
    semantic_basis: "长上下文、复杂推理和事实可靠性共同形成科研分析能力链。"
    kl_constraints:
      focus_mass_minimum: "sum(w_C1,w_C3) >= alpha"
      lower_bounds: {C2: 0.20}
      order_constraints: []
    alpha_range: [0.60, 0.75]
    alpha_reference: 0.675
    alpha_grid_size: 9
    rho_range: [-0.80, -0.20]
    rho_reference: -0.50
    rho_grid_size: 13
  dialogue:
    label: "大众日常通用对话"
    ces_core_dimensions: [C1, C2, C3, C5]
    kl_focus_dimensions: [C1, C2]
    semantic_basis: "推理与事实可靠性构成即时对话主轴，长上下文和多模态维持连续交互与输入覆盖。"
    kl_constraints:
      focus_mass_minimum: "sum(w_C1,w_C2) >= alpha"
      lower_bounds: {C3: 0.10, C5: 0.10}
      order_constraints: []
    alpha_range: [0.55, 0.70]
    alpha_reference: 0.625
    alpha_grid_size: 9
    rho_range: [-0.30, 0.30]
    rho_reference: 0.00
    rho_grid_size: 13
  coding:
    label: "计算机代码开发"
    ces_core_dimensions: [C1, C4]
    kl_focus_dimensions: [C4]
    semantic_basis: "代码与软件工程能力是直接产出能力，复杂推理负责需求分解、调试和方案选择。"
    kl_constraints:
      focus_mass_minimum: "w_C4 >= alpha"
      lower_bounds: {}
      order_constraints: []
    alpha_range: [0.55, 0.75]
    alpha_reference: 0.65
    alpha_grid_size: 9
    rho_range: [-0.70, -0.10]
    rho_reference: -0.40
    rho_grid_size: 13

kl_priors:
  primary:
    name: "Q1 objective prior"
    source: "q2/data/q1_dimension_weights_reference.csv"
    interpretation: "Q1 information contribution, non-redundancy, and stability; restricted and renormalized on each scene core."
  robustness:
    name: "Equal prior"
    definition: "Uniform on each scene core."

ces_input_transform:
  primary:
    name: "BT latent strength"
    formula: "z_ij = exp(theta_ij - max_i(theta_ij))"
    properties: [strictly_positive, monotone, dimensionwise_bounded_by_one]
    source: "q2/data/q1_bt_latent_scores.csv"
  sensitivity:
    name: "Positive-floor score mapping"
    formula: "z_ij = delta + (1-delta) * S_ij / 100"
    delta_reference: 0.20
    delta_grid: [0.10, 0.15, 0.20, 0.25, 0.30]
    source: "q2/data/q1_capability_scores.csv"

c5_structural_absence:
  policy: "structural availability anchor; never benchmark zero and never latent-score imputation"
  primary_anchor: 0.35
  sensitivity_grid: [0.20, 0.275, 0.35, 0.425, 0.50]
  common_dimension_check: "Recompute dialogue without C5 on C1-C3."
  source: "q2/data/q1_model_applicability.csv"

uncertainty_propagation:
  source: "q2/data/q1_uncertainty.csv"
  scope: "DIMENSION_LATENT_SCORE"
  approximation: "theta_draw = point_theta + Normal(0, theta_bootstrap_sd); structural C5 anchors remain fixed"
  covariance_note: "Cross-model and cross-dimension covariance is unavailable in the standardized interface; independent draws are used and disclosed."
  draws: 2000
  random_seed: 20260817
  reported_statistics: [utility_ci_2_5, utility_ci_97_5, probability_rank_1, probability_top_3]

reference_results:
  ranking_method: "competition rank (method=min), descending utility"
  q1_rank_baseline: "Q1 Ranking A all-model reference ranking"
  linear_baseline: "Same KL weights and transformed inputs; complete compensation"
  pri_definition: "(linear_utility - ces_utility) / linear_utility"
  nonlinear_explanation: [ces_inner_share, marginal_utility, utility_elasticity]

outputs:
  machine_readable_directory: "outputs/q2/final"
  figure_directory: "figures/q2"
  standalone_pdf: "output/pdf/Q2_Final_Paper.pdf"
~~~~

## 5.4 Q3 成本-Pareto 数学模块

以下完整模块实现成本、队列、Pareto、预算、ICER、拟合、敏感性和数据校验计算。

### `q3/src/__init__.py`

~~~~python
"""Q3 cost-utility decision framework."""
~~~~

### `q3/src/budget_selection.py`

~~~~python
from __future__ import annotations

import math

import pandas as pd


def _choose_best(feasible: pd.DataFrame) -> pd.Series | None:
    if feasible.empty:
        return None
    ordered = feasible.sort_values(["utility", "cost", "model_id"], ascending=[False, True, True])
    return ordered.iloc[0]


def compute_budget_frontier(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    complete = df.dropna(subset=["utility", "cost"]).copy()
    for scenario, group in complete.groupby("scenario", dropna=False):
        costs = sorted(group["cost"].dropna().unique())
        if not costs:
            rows.append({"scenario": scenario, "budget_lower": 0.0, "budget_upper": math.inf, "optimal_model_id": "NO_FEASIBLE_MODEL"})
            continue
        first_cost = float(costs[0])
        if first_cost > 0:
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": 0.0,
                    "budget_upper": first_cost,
                    "optimal_model_id": "NO_FEASIBLE_MODEL",
                    "optimal_model_name": "NO_FEASIBLE_MODEL",
                    "utility": pd.NA,
                    "cost": pd.NA,
                }
            )
        for idx, cost in enumerate(costs):
            upper = float(costs[idx + 1]) if idx + 1 < len(costs) else math.inf
            best = _choose_best(group[group["cost"] <= cost])
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": float(cost),
                    "budget_upper": upper,
                    "optimal_model_id": best["model_id"] if best is not None else "NO_FEASIBLE_MODEL",
                    "optimal_model_name": best.get("model_name", best.get("model", "")) if best is not None else "NO_FEASIBLE_MODEL",
                    "utility": best["utility"] if best is not None else pd.NA,
                    "cost": best["cost"] if best is not None else pd.NA,
                }
            )
    if complete.empty:
        for scenario in sorted(df["scenario"].dropna().unique()):
            rows.append(
                {
                    "scenario": scenario,
                    "budget_lower": 0.0,
                    "budget_upper": math.inf,
                    "optimal_model_id": "NO_FEASIBLE_MODEL",
                    "optimal_model_name": "NO_FEASIBLE_MODEL",
                    "utility": pd.NA,
                    "cost": pd.NA,
                }
            )
    return pd.DataFrame(rows)


def save_budget_selection(input_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    result = compute_budget_frontier(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
~~~~

### `q3/src/cohort.py`

~~~~python
from __future__ import annotations

from pathlib import Path

import pandas as pd


COHORT_ORDER = ["FULL", "PARTIAL", "MISSING"]


def build_analysis_cohort(
    pricing: pd.DataFrame,
    pricing_audit: pd.DataFrame,
    utilities: pd.DataFrame | None = None,
    pricing_human_check: pd.DataFrame | None = None,
) -> pd.DataFrame:
    price = pricing.copy()
    audit = pricing_audit.copy()
    price["input_price_num"] = pd.to_numeric(price.get("input_price"), errors="coerce")
    price["output_price_num"] = pd.to_numeric(price.get("output_price"), errors="coerce")

    audit_fields = [
        "model_id",
        "pricing_status",
        "fallback_issue",
        "fallback_rate",
        "sku_mapping_status",
        "config_mapping_status",
        "human_verified",
    ]
    audit_use = audit[[col for col in audit_fields if col in audit.columns]].drop_duplicates("model_id")
    merged = price.merge(audit_use, on="model_id", how="left", suffixes=("", "_audit"))
    if pricing_human_check is not None and not pricing_human_check.empty and "model_id" in pricing_human_check.columns:
        check = pricing_human_check[[col for col in ["model_id", "human_verified"] if col in pricing_human_check.columns]].drop_duplicates("model_id")
        merged = merged.merge(check, on="model_id", how="left", suffixes=("", "_human_check"))

    utility_ids = set()
    if utilities is not None and not utilities.empty and "model_id" in utilities.columns:
        utility_ids = set(utilities["model_id"].astype(str))

    rows = []
    for _, row in merged.iterrows():
        model_id = str(row["model_id"])
        pricing_status = str(row.get("pricing_status", ""))
        has_base_price = pd.notna(row["input_price_num"]) and pd.notna(row["output_price_num"])
        fallback_issue = str(row.get("fallback_issue", "")).upper() == "TRUE"
        verified_fields = [
            str(row.get("human_verified", "")).upper() == "TRUE",
            str(row.get("human_verified_audit", "")).upper() == "TRUE",
            str(row.get("human_verified_human_check", "")).upper() == "TRUE",
        ]
        pricing_human_verified = all(verified_fields)
        if pricing_status == "READY" and has_base_price and not fallback_issue:
            observability = "FULL"
            included = pricing_human_verified
            exclusion_reason = "" if included else "complete price is present but all human-verification records are not TRUE"
        elif has_base_price:
            observability = "PARTIAL"
            included = False
            exclusion_reason = "base model price exists but benchmark configuration has unresolved special billing"
        else:
            observability = "MISSING"
            included = False
            exclusion_reason = "official input/output price is missing or not publicly observable"

        rows.append(
            {
                "model_id": model_id,
                "model_name": row.get("model_name", ""),
                "utility_available": model_id in utility_ids,
                "pricing_available": has_base_price,
                "pricing_human_verified": pricing_human_verified,
                "cost_observability": observability,
                "pricing_status": pricing_status,
                "sku_mapping_status": row.get("sku_mapping_status", ""),
                "config_mapping_status": row.get("config_mapping_status", ""),
                "fallback_issue": str(row.get("fallback_issue", "")),
                "fallback_rate": row.get("fallback_rate", ""),
                "included_in_main_pareto": included,
                "included_in_regression": included,
                "exclusion_reason": exclusion_reason,
            }
        )

    result = pd.DataFrame(rows)
    result["cost_observability"] = pd.Categorical(result["cost_observability"], categories=COHORT_ORDER, ordered=True)
    return result.sort_values(["cost_observability", "model_id"]).reset_index(drop=True)


def full_model_ids(cohort: pd.DataFrame) -> list[str]:
    included = cohort["included_in_main_pareto"].astype(str).str.upper().eq("TRUE")
    return cohort.loc[
        (cohort["cost_observability"].astype(str) == "FULL") & included,
        "model_id",
    ].astype(str).tolist()


def attach_cost_observability(costs: pd.DataFrame, cohort: pd.DataFrame) -> pd.DataFrame:
    fields = ["model_id", "cost_observability", "included_in_main_pareto", "exclusion_reason"]
    return costs.merge(cohort[fields], on="model_id", how="left")


def save_analysis_cohort(cohort: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = cohort.copy()
    output["cost_observability"] = output["cost_observability"].astype(str)
    output.to_csv(output_path, index=False)
    return output
~~~~

### `q3/src/cost_model.py`

~~~~python
from __future__ import annotations

from pathlib import Path

import pandas as pd


PRICE_UNIT = "USD / 1M billable tokens"


def _to_number(value):
    if pd.isna(value) or value == "" or str(value).upper() == "NA":
        return pd.NA
    return pd.to_numeric(value, errors="coerce")


def compute_scenario_cost(model_price: dict, workload: dict) -> dict:
    """Compute one model-scenario workload cost using prices in USD / 1M billable tokens."""
    input_price = _to_number(model_price.get("input_price"))
    output_price = _to_number(model_price.get("output_price"))
    n_calls = _to_number(workload.get("n_calls"))
    input_tokens = _to_number(workload.get("input_tokens"))
    output_tokens = _to_number(workload.get("output_tokens"))

    if any(pd.isna(x) for x in [input_price, output_price, n_calls, input_tokens, output_tokens]):
        return {"input_cost": pd.NA, "output_cost": pd.NA, "cost": pd.NA}

    input_cost = float(n_calls) * float(input_tokens) * float(input_price) / 1_000_000
    output_cost = float(n_calls) * float(output_tokens) * float(output_price) / 1_000_000
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "cost": input_cost + output_cost,
    }


def compute_all_costs(
    pricing: pd.DataFrame,
    workloads: pd.DataFrame,
    utilities: pd.DataFrame | None = None,
    workload_level: str = "baseline_template",
) -> pd.DataFrame:
    workloads_use = workloads.copy()
    if workload_level is not None and "workload_level" in workloads_use.columns:
        workloads_use = workloads_use[workloads_use["workload_level"] == workload_level]

    rows = []
    utility_lookup = {}
    if utilities is not None and not utilities.empty:
        for _, row in utilities.iterrows():
            utility_lookup[(row.get("model_id"), row.get("scenario"))] = row.get("utility")

    for _, model_row in pricing.iterrows():
        for _, workload_row in workloads_use.iterrows():
            costs = compute_scenario_cost(model_row.to_dict(), workload_row.to_dict())
            rows.append(
                {
                    "model_id": model_row.get("model_id"),
                    "model_name": model_row.get("model_name"),
                    "scenario": workload_row.get("scenario"),
                    "workload_level": workload_row.get("workload_level"),
                    "utility": utility_lookup.get((model_row.get("model_id"), workload_row.get("scenario")), pd.NA),
                    **costs,
                }
            )
    return pd.DataFrame(rows)


def load_and_compute(
    pricing_path: Path,
    workload_path: Path,
    utility_path: Path | None,
    output_path: Path,
    workload_level: str = "baseline_template",
) -> pd.DataFrame:
    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    workloads = pd.read_csv(workload_path, keep_default_na=False)
    utilities = None
    if utility_path is not None and utility_path.exists():
        utilities = pd.read_csv(utility_path, keep_default_na=False)
        utilities["utility"] = pd.to_numeric(utilities.get("utility"), errors="coerce")
        utilities = utilities.dropna(subset=["utility"])
    result = compute_all_costs(pricing, workloads, utilities, workload_level=workload_level)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
~~~~

### `q3/src/cost_performance_fit.py`

~~~~python
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def _metrics(y, yhat, k: int) -> dict:
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    n = len(y)
    rss = float(np.sum((y - yhat) ** 2))
    tss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = np.nan if tss == 0 else 1 - rss / tss
    sigma2 = max(rss / n, 1e-12)
    aic = n * math.log(sigma2) + 2 * k
    aicc = np.nan if n <= k + 1 else aic + (2 * k * (k + 1)) / (n - k - 1)
    bic = n * math.log(sigma2) + k * math.log(n)
    return {"n": n, "rss": rss, "r2": r2, "aic": aic, "aicc": aicc, "bic": bic}


def _fit_linear(x, y):
    x_design = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    return coef, x_design @ coef


def _fit_log(x, y):
    z = np.log1p(x)
    x_design = np.column_stack([np.ones(len(z)), z])
    coef, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    return coef, x_design @ coef


def _saturation(x, a, b, k):
    return a - b * np.exp(-k * x)


def _loocv_error(x, y, model_name: str) -> float:
    if len(y) <= 3:
        return np.nan
    errors = []
    for idx in range(len(y)):
        mask = np.ones(len(y), dtype=bool)
        mask[idx] = False
        try:
            pred = _predict_one(x[mask], y[mask], np.array([x[idx]]), model_name)[0]
            errors.append((y[idx] - pred) ** 2)
        except Exception:
            return np.nan
    return float(np.mean(errors))


def _predict_one(x_train, y_train, x_pred, model_name: str):
    if model_name == "linear":
        coef, _ = _fit_linear(x_train, y_train)
        return np.column_stack([np.ones(len(x_pred)), x_pred]) @ coef
    if model_name == "log":
        coef, _ = _fit_log(x_train, y_train)
        return np.column_stack([np.ones(len(x_pred)), np.log1p(x_pred)]) @ coef
    popt, _ = curve_fit(_saturation, x_train, y_train, p0=[float(np.max(y_train)), float(np.ptp(y_train) or 1.0), 1.0], maxfev=10000)
    return _saturation(x_pred, *popt)


def fit_cost_performance(df: pd.DataFrame, subset_label: str = "all_models") -> pd.DataFrame:
    rows = []
    complete = df.dropna(subset=["utility", "cost"]).copy()
    for scenario, group in complete.groupby("scenario", dropna=False):
        x = group["cost"].astype(float).to_numpy()
        y = group["utility"].astype(float).to_numpy()
        if len(group) < 3:
            continue
        for model_name, fitter, k_params in [
            ("linear", _fit_linear, 2),
            ("log", _fit_log, 2),
        ]:
            coef, yhat = fitter(x, y)
            rows.append(
                {
                    "scenario": scenario,
                    "subset": subset_label,
                    "fit_model": model_name,
                    "parameters": ";".join(f"{v:.12g}" for v in coef),
                    "loocv_error": _loocv_error(x, y, model_name),
                    **_metrics(y, yhat, k_params),
                }
            )
        if len(group) >= 4 and np.ptp(x) > 0:
            try:
                popt, _ = curve_fit(_saturation, x, y, p0=[float(np.max(y)), float(np.ptp(y) or 1.0), 1.0], maxfev=10000)
                yhat = _saturation(x, *popt)
                rows.append(
                    {
                        "scenario": scenario,
                        "subset": subset_label,
                        "fit_model": "saturation",
                        "parameters": ";".join(f"{v:.12g}" for v in popt),
                        "loocv_error": _loocv_error(x, y, "saturation"),
                        **_metrics(y, yhat, 3),
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "scenario": scenario,
                        "subset": subset_label,
                        "fit_model": "saturation",
                        "parameters": "",
                        "loocv_error": np.nan,
                        "n": len(group),
                        "rss": np.nan,
                        "r2": np.nan,
                        "aic": np.nan,
                        "aicc": np.nan,
                        "bic": np.nan,
                        "fit_note": f"fit failed: {exc}",
                    }
                )
    return pd.DataFrame(rows)


def save_fit_reports(cost_utility_path, pareto_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(cost_utility_path)
    frames = [fit_cost_performance(df, "all_models")]
    if pareto_path.exists():
        pareto = pd.read_csv(pareto_path)
        frames.append(fit_cost_performance(pareto[pareto["pareto"] == True], "pareto_frontier"))
    result = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True) if any(not f.empty for f in frames) else pd.DataFrame()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
~~~~

### `q3/src/incremental_cost.py`

~~~~python
from __future__ import annotations

import math

import pandas as pd


def compute_icer(pareto_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    front = pareto_df[(pareto_df["pareto"] == True)].dropna(subset=["utility", "cost"]).copy()
    for scenario, group in front.groupby("scenario", dropna=False):
        ordered = group.sort_values(["cost", "utility", "model_id"], ascending=[True, True, True]).reset_index(drop=True)
        for idx in range(len(ordered) - 1):
            a = ordered.iloc[idx]
            b = ordered.iloc[idx + 1]
            delta_cost = float(b["cost"]) - float(a["cost"])
            delta_utility = float(b["utility"]) - float(a["utility"])
            if delta_utility == 0:
                icer = math.inf if delta_cost > 0 else pd.NA
            else:
                icer = delta_cost / delta_utility
            rows.append(
                {
                    "scenario": scenario,
                    "from_model": a["model_id"],
                    "to_model": b["model_id"],
                    "delta_cost": delta_cost,
                    "delta_utility": delta_utility,
                    "icer": icer,
                }
            )
    return pd.DataFrame(rows)


def save_icer(pareto_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(pareto_path)
    result = compute_icer(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
~~~~

### `q3/src/pareto_analysis.py`

~~~~python
from __future__ import annotations

import pandas as pd


def _complete(row) -> bool:
    return pd.notna(row.get("utility")) and pd.notna(row.get("cost"))


def dominates(candidate, target) -> bool:
    if not _complete(candidate) or not _complete(target):
        return False
    better_or_equal_utility = float(candidate["utility"]) >= float(target["utility"])
    cheaper_or_equal = float(candidate["cost"]) <= float(target["cost"])
    strictly_better = float(candidate["utility"]) > float(target["utility"]) or float(candidate["cost"]) < float(target["cost"])
    return better_or_equal_utility and cheaper_or_equal and strictly_better


def compute_pareto_frontier(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario, group in df.groupby("scenario", dropna=False):
        records = group.to_dict("records")
        for row in records:
            dominators = [other["model_id"] for other in records if dominates(other, row)]
            missing = not _complete(row)
            rows.append(
                {
                    **row,
                    "pareto": False if missing else len(dominators) == 0,
                    "dominated_by": ";".join(dominators),
                    "dominance_count": len(dominators),
                    "pareto_status_note": "missing utility or cost" if missing else "complete",
                }
            )
    return pd.DataFrame(rows)


def save_pareto(input_path, output_path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    result = compute_pareto_frontier(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def compute_bootstrap_pareto_probability(bootstrap_utility: pd.DataFrame, cost_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate P(model in Pareto frontier) when Q2 bootstrap utility samples exist."""
    if bootstrap_utility.empty:
        return pd.DataFrame(columns=["model_id", "scenario", "pareto_probability"])
    required = {"model_id", "scenario", "bootstrap_id", "utility"}
    if not required.issubset(bootstrap_utility.columns):
        raise ValueError(f"Bootstrap utility must contain {sorted(required)}")
    cost_lookup = cost_df[["model_id", "scenario", "cost"]].drop_duplicates()
    merged = bootstrap_utility.merge(cost_lookup, on=["model_id", "scenario"], how="left")
    rows = []
    for (scenario, bootstrap_id), group in merged.groupby(["scenario", "bootstrap_id"], dropna=False):
        pareto = compute_pareto_frontier(group)
        for _, row in pareto.iterrows():
            rows.append({"scenario": scenario, "bootstrap_id": bootstrap_id, "model_id": row["model_id"], "pareto": row["pareto"]})
    if not rows:
        return pd.DataFrame(columns=["model_id", "scenario", "pareto_probability"])
    probs = pd.DataFrame(rows).groupby(["model_id", "scenario"], as_index=False)["pareto"].mean()
    return probs.rename(columns={"pareto": "pareto_probability"})
~~~~

### `q3/src/sensitivity_analysis.py`

~~~~python
from __future__ import annotations

import pandas as pd

from budget_selection import compute_budget_frontier
from cost_model import compute_all_costs
from pareto_analysis import compute_pareto_frontier


def input_scale_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, scales=(0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows = []
    baseline = workload[workload["workload_level"] == "baseline_template"].copy()
    for scale in scales:
        varied = baseline.copy()
        varied["input_tokens"] = pd.to_numeric(varied["input_tokens"], errors="coerce") * scale
        varied["workload_level"] = f"input_scale_{scale:g}"
        costs = compute_all_costs(pricing, varied, utilities, workload_level=None)
        pareto = compute_pareto_frontier(costs)
        budget = compute_budget_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "input_scale", "parameter": scale, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
        for _, row in budget.iterrows():
            rows.append({"analysis": "input_scale_budget", "parameter": scale, "scenario": row["scenario"], "model_id": row["optimal_model_id"], "cost": row.get("cost"), "utility": row.get("utility"), "pareto": pd.NA})
    return pd.DataFrame(rows)


def ratio_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, ratios=(0.1, 0.3, 0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows = []
    baseline = workload[workload["workload_level"] == "baseline_template"].copy()
    for ratio in ratios:
        varied = baseline.copy()
        varied["input_tokens"] = pd.to_numeric(varied["input_tokens"], errors="coerce")
        varied["output_tokens"] = varied["input_tokens"] * ratio
        varied["input_output_ratio"] = ratio
        varied["workload_level"] = f"ratio_{ratio:g}"
        costs = compute_all_costs(pricing, varied, utilities, workload_level=None)
        pareto = compute_pareto_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "input_output_ratio", "parameter": ratio, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
    return pd.DataFrame(rows)


def price_perturbation_sensitivity(pricing: pd.DataFrame, workload: pd.DataFrame, utilities: pd.DataFrame | None, deltas=(-0.1, -0.05, 0.0, 0.05, 0.1)) -> pd.DataFrame:
    rows = []
    for delta in deltas:
        varied = pricing.copy()
        for col in ["input_price", "output_price", "cached_input_price"]:
            if col in varied.columns:
                nums = pd.to_numeric(varied[col], errors="coerce")
                varied[col] = nums * (1 + delta)
        costs = compute_all_costs(varied, workload, utilities, workload_level="baseline_template")
        pareto = compute_pareto_frontier(costs)
        budget = compute_budget_frontier(costs)
        for _, row in pareto.iterrows():
            rows.append({"analysis": "price_perturbation", "parameter": delta, "scenario": row["scenario"], "model_id": row["model_id"], "cost": row["cost"], "utility": row["utility"], "pareto": row["pareto"]})
        for _, row in budget.iterrows():
            rows.append({"analysis": "price_perturbation_budget", "parameter": delta, "scenario": row["scenario"], "model_id": row["optimal_model_id"], "cost": row.get("cost"), "utility": row.get("utility"), "pareto": pd.NA})
    return pd.DataFrame(rows)


def _as_dataframe(value, **read_csv_kwargs) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return pd.read_csv(value, **read_csv_kwargs)


def run_sensitivity(pricing_path, workload_path, utility_path, output_path) -> pd.DataFrame:
    pricing = _as_dataframe(pricing_path, keep_default_na=False)
    workload = _as_dataframe(workload_path, keep_default_na=False)
    utilities = None
    if utility_path is not None and (isinstance(utility_path, pd.DataFrame) or utility_path.exists()):
        utilities = _as_dataframe(utility_path, keep_default_na=False)
        utilities["utility"] = pd.to_numeric(utilities.get("utility"), errors="coerce")
        utilities = utilities.dropna(subset=["utility"])
    result = pd.concat(
        [
            input_scale_sensitivity(pricing, workload, utilities),
            ratio_sensitivity(pricing, workload, utilities),
            price_perturbation_sensitivity(pricing, workload, utilities),
        ],
        ignore_index=True,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
~~~~

### `q3/src/validate_q3_data.py`

~~~~python
from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_PRICING_COLUMNS = [
    "model_id",
    "model_name",
    "exact_version",
    "provider",
    "price_date",
    "input_price",
    "output_price",
    "cached_input_price",
    "price_unit",
    "deployment",
    "source_type",
    "source_url",
    "human_verified",
    "notes",
]
REQUIRED_UTILITY_COLUMNS = ["model_id", "model_name", "scenario", "utility"]
REQUIRED_WORKLOAD_COLUMNS = ["scenario", "scenario_name", "n_calls", "input_tokens", "output_tokens", "input_output_ratio", "workload_level", "source_or_rationale", "notes"]
PRICE_UNIT = "USD / 1M billable tokens"


def _issue(issues, severity, file, field, model_id, message):
    issues.append({"severity": severity, "file": file, "field": field, "model_id": model_id, "message": message})


def _num(series):
    return pd.to_numeric(series.replace({"NA": pd.NA, "": pd.NA}), errors="coerce")


def validate_q3_data(pricing_path: Path, workload_path: Path, utility_path: Path, q2_master_path: Path, report_path: Path) -> pd.DataFrame:
    issues = []
    pricing = pd.read_csv(pricing_path, keep_default_na=False)
    workload = pd.read_csv(workload_path, keep_default_na=False)
    q2_master = pd.read_csv(q2_master_path, keep_default_na=False) if q2_master_path.exists() else pd.DataFrame()
    utility = pd.read_csv(utility_path, keep_default_na=False) if utility_path.exists() else pd.DataFrame(columns=REQUIRED_UTILITY_COLUMNS)

    for col in REQUIRED_PRICING_COLUMNS:
        if col not in pricing.columns:
            _issue(issues, "ERROR", str(pricing_path), col, "", "Missing required pricing column")
    for col in REQUIRED_WORKLOAD_COLUMNS:
        if col not in workload.columns:
            _issue(issues, "ERROR", str(workload_path), col, "", "Missing required workload column")
    for col in REQUIRED_UTILITY_COLUMNS:
        if col not in utility.columns:
            _issue(issues, "ERROR", str(utility_path), col, "", "Missing required utility column")

    if "model_id" in pricing.columns:
        dupes = pricing[pricing["model_id"].duplicated(keep=False)]
        for _, row in dupes.iterrows():
            _issue(issues, "ERROR", str(pricing_path), "model_id", row["model_id"], "Duplicate pricing model_id")

    if not q2_master.empty and "model_id" in pricing.columns:
        q2_ids = set(q2_master["model_id"])
        q3_ids = set(pricing["model_id"])
        for model_id in sorted(q2_ids - q3_ids):
            _issue(issues, "ERROR", str(pricing_path), "model_id", model_id, "Q2 model missing from Q3 pricing table")
        for model_id in sorted(q3_ids - q2_ids):
            _issue(issues, "ERROR", str(pricing_path), "model_id", model_id, "Q3 pricing model not present in Q2 master table")
        merged = pricing.merge(q2_master[["model_id", "model"]], on="model_id", how="inner")
        mismatched = merged[merged["model_name"] != merged["model"]]
        for _, row in mismatched.iterrows():
            _issue(issues, "WARNING", str(pricing_path), "model_name", row["model_id"], f"Model name differs from Q2: {row['model_name']} != {row['model']}")

    if "price_unit" in pricing.columns:
        bad_unit = pricing[pricing["price_unit"] != PRICE_UNIT]
        for _, row in bad_unit.iterrows():
            _issue(issues, "ERROR", str(pricing_path), "price_unit", row.get("model_id", ""), "Price unit must be USD / 1M billable tokens")

    for col in ["input_price", "output_price", "cached_input_price"]:
        if col in pricing.columns:
            nums = _num(pricing[col])
            negative = pricing[nums < 0]
            for _, row in negative.iterrows():
                _issue(issues, "ERROR", str(pricing_path), col, row.get("model_id", ""), "Price must be non-negative")
            missing = pricing[nums.isna()]
            for _, row in missing.iterrows():
                if col == "cached_input_price":
                    severity = "WARNING"
                    message = "Cached-input price is unavailable; baseline uses uncached input pricing"
                else:
                    severity = "COHORT_EXCLUDED"
                    message = "Input/output price is unavailable; model is excluded from the FULL-cost cohort without imputation"
                _issue(issues, severity, str(pricing_path), col, row.get("model_id", ""), message)

    for col in ["price_date", "source_url", "exact_version"]:
        if col in pricing.columns:
            missing = pricing[pricing[col].isin(["", "NA"])]
            for _, row in missing.iterrows():
                _issue(issues, "BLOCKING_INPUT_MISSING", str(pricing_path), col, row.get("model_id", ""), f"{col} is missing")

    if {"model_id", "price_date"}.issubset(pricing.columns):
        multi_dates = pricing.groupby("model_id")["price_date"].nunique(dropna=False)
        for model_id, count in multi_dates.items():
            if count > 1:
                _issue(issues, "WARNING", str(pricing_path), "price_date", model_id, "Multiple price dates found for the same model")

    for col in ["n_calls", "input_tokens", "output_tokens"]:
        if col in workload.columns:
            nums = pd.to_numeric(workload[col], errors="coerce")
            bad = workload[nums <= 0]
            for _, row in bad.iterrows():
                _issue(issues, "ERROR", str(workload_path), col, row.get("scenario", ""), "Workload value must be positive")

    if not utility.empty and "utility" in utility.columns:
        util = pd.to_numeric(utility["utility"], errors="coerce")
        supplied = utility[utility["utility"].astype(str).str.strip() != ""]
        bad = supplied[util.loc[supplied.index].isna() | (util.loc[supplied.index] < 0) | (util.loc[supplied.index] > 100)]
        for _, row in bad.iterrows():
            _issue(issues, "ERROR", str(utility_path), "utility", row.get("model_id", ""), "Utility must be numeric and in [0, 100]")
        if supplied.empty:
            _issue(issues, "BLOCKING_INPUT_MISSING", str(utility_path), "utility", "", "No Q2 scenario utility values supplied")
    else:
        _issue(issues, "BLOCKING_INPUT_MISSING", str(utility_path), "utility", "", "No Q2 scenario utility file found")

    report = pd.DataFrame(issues, columns=["severity", "file", "field", "model_id", "message"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path, index=False)
    hard = report[report["severity"] == "ERROR"] if not report.empty else pd.DataFrame()
    if not hard.empty:
        raise ValueError(f"Q3 validation failed with {len(hard)} ERROR issue(s). See {report_path}")
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    validate_q3_data(
        root / "q3" / "data" / "model_pricing.csv",
        root / "q3" / "data" / "workload_config.csv",
        root / "q3" / "data" / "scenario_utility.csv",
        root / "q2" / "data" / "q2_model_master_table.csv",
        root / "q3" / "outputs" / "diagnostics" / "q3_data_validation_report.csv",
    )
~~~~


## 六、复现与真实性说明

- 建议使用 Python 3.11/3.12，并执行 `python -m pip install -r requirements.txt`；Q1 原始表格代码要求 `pandas<3.0`。
- Q1 冻结输入的字节校验依赖仓库 CRLF 行尾策略；应使用 Git checkout/worktree，不应以 GitHub ZIP 的 LF 文件重算冻结哈希。
- Q2 独立重跑产生 30 行名义场景效用和 60,000 行 Bootstrap 接口，Q2→Q3 的 18 项校验通过。
- Q3 论文对应的模型结果一致性 43 项通过；本机重跑的成本--性能拟合最大绝对浮点差为 `1.42109e-14`，不影响 Pareto 节点或预算阈值。
- 数学模型使用 Python 计算；Excel/XLSX 用于承载模型输入、数值结果和人工审计记录。
