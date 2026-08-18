# final_paper_v3 支撑材料说明

## 1. 内容范围

本压缩包汇集支撑 Q1--Q3 数学模型、数值结果与结论的建模程序、外部数据、模型接口、中间结果和关键图表。赛题正文及赛题提供的原始材料不在本压缩包中重复收录。

## 2. 目录说明

- `src/q1/`：Q1 数据读取、相关性、Bradley--Terry、客观赋权、综合评分、Bootstrap、LOFO/LOSO 和冻结校验程序；
- `src/q2/` 与 `q2/model_spec_v1.yaml`：Q2 KL 投影、CES 效用、缺失策略、边际分析、不确定性传播和敏感性程序；
- `q3/src/`：Q3 成本、Pareto、预算选择、ICER、成本--性能拟合和敏感性程序；
- `frozen/v1.0/`、`q2/data/`、`q3/data/`、`q3/frozen/v1.0/`：自主查阅形成的 Benchmark、来源登记、价格、工作负载和跨问题接口数据；
- `outputs/`、`q2/outputs/`、`q3/outputs/`：模型数值结果、Bootstrap、稳健性和诊断输出；
- `figures/q1/`、`figures/q2/`、`figures/q3/`：支撑模型结果与结论的关键中间结果图表；
- `requirements.txt`：Python 建模依赖；
- `支撑材料文件清单.csv`：压缩包逐文件类别、用途、大小和 SHA-256；
- `SHA256SUMS.txt`：文件完整性校验值。

## 3. 运行环境

建议使用 Python 3.11 或 3.12，在本目录执行：

    python -m pip install -r requirements.txt

Q1 正式设置为 Bootstrap 2,000 次、随机种子 20260817；Q1 表格接口需要 `pandas<3.0`。数学模型使用 Python 计算，XLSX 文件用于承载输入、结果和人工审核记录。

## 4. 数据真实性口径

Q1 冻结文件的 SHA-256 以 Git checkout/worktree 保留的仓库行尾为准。Q3 对 Claude Fable 5 保持 `PARTIAL`，对 GLM-5.2 保持 `MISSING`，没有补造缺失价格。所有文件的最终校验值以本包内 `支撑材料文件清单.csv` 为准。
