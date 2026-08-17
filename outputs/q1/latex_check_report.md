# 问题一 LaTeX 排版检查报告

## 1. 正文使用的表

1. 表1：模型数据覆盖情况，依据 `outputs/q1/tables/paper_table_2_data_coverage.xlsx`。
2. 表2：C1--C5 与 Benchmark Family 指标体系，依据 `outputs/q1/tables/paper_table_1_indicator_system.xlsx`。
3. 表3：Benchmark Family 相关性与筛选结果，依据 `outputs/q1/tables/paper_table_3_correlation_screening.xlsx`。
4. 表4：各模型五维能力得分，依据 `outputs/q1/tables/paper_table_4_dimension_scores.xlsx`。
5. 表5：五维能力客观权重及其构成，依据 `outputs/q1/tables/paper_table_5_dimension_weights.xlsx`。
6. 表6：十款大语言模型综合得分与排名，依据 `outputs/q1/tables/paper_table_6_overall_ranking.xlsx`。
7. 表7：Kimi K3 的 Bootstrap 和敏感性结果，依据 `outputs/q1/tables/paper_table_7_kimi_comparison.xlsx` 与 `outputs/q1/tables/paper_table_8_robustness.xlsx`。

## 2. 正文使用的图

1. 图1：问题一综合评价模型总体框架，文件 `outputs/q1/figures/figure_q1_00_model_framework.png`。
2. 图2：模型--Exact Setting 数据覆盖热力图，文件 `outputs/q1/figures/figure_q1_01_coverage_heatmap.png`。
3. 图3：Benchmark Family 缺失感知 Spearman 相关热力图，文件 `outputs/q1/figures/figure_q1_02_spearman_heatmap.png`。
4. 图4：各模型五维能力得分热力图，文件 `outputs/q1/figures/figure_q1_04_dimension_scores.png`。
5. 图5：综合得分及 95% Bootstrap 置信区间，文件 `outputs/q1/figures/figure_q1_05_overall_score_ci.png`。
6. 图6：Bootstrap 排名稳定性，文件 `outputs/q1/figures/figure_q1_06_rank_stability.png`。
7. 图7：Leave-One-Family-Out 排名变化，文件 `outputs/q1/figures/figure_q1_07_lofo_rank_change.png`。
8. 图8：Kimi K3 相对于有效模型中位数的能力差值，文件 `outputs/q1/figures/figure_q1_10_kimi_advantage_gap.png`。

## 3. 附录候选图

1. `outputs/q1/figures/figure_q1_03_common_n_heatmap.png`：共同样本数热力图，适合放入附录作为 Spearman 相关性的样本量支撑。
2. `outputs/q1/figures/figure_q1_08_sensitivity_rank.png`：敏感性排名热力图，正文已用表7概括关键情景，可放附录。
3. `outputs/q1/figures/figure_q1_09_kimi_profile.png`：Kimi K3 五维雷达图，正文采用差值图表达优势/短板，雷达图可放附录。

## 4. 数字核对与修改

- 已核对 `README_Q1.md`、`outputs/q1/results_summary.md`、`outputs/q1/results_summary.json`、`outputs/q1/diagnostics/model_diagnostics.json` 以及全部 `paper_table_*.xlsx`。
- 未发现 `q1_draft.md` 中核心结果与正式输出冲突。
- 正文采用正式输出中的舍入值：综合得分保留三位小数，权重保留四位小数。
- C5 缺失项在表4和表6中显示为 `--`，未按 0 分处理。

## 5. 编译与引用检查

- 编译命令：`xelatex -interaction=nonstopmode -halt-on-error main.tex`，已连续成功编译。
- 所有公式成功编译。
- 所有 figure/table reference 已解析成功。
- 未发现 missing reference。
- 未发现 `Overfull \hbox`。
- 最终 PDF 已成功生成：`main.pdf`。

## 6. 视觉检查

- 使用 `pdftocairo` 将 `main.pdf` 渲染为 PNG 页面并制作联系表检查。
- 页面渲染文件位于 `outputs/q1/latex_pages/`。
- 检查结果：图表均正常显示，链接边框已隐藏，未发现空白图片或明显表格断裂。

## 7. 备注

- 本次未修改 `frozen/v1.0`。
- 未重新采集数据，未重新定义 C1--C5，未替换正式模型路线。
- `pdftoppm` 封装命令在当前环境中提示路径不可用，已改用可用的 `pdftocairo` 完成 PDF 渲染检查。
