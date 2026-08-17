# Submission Supporting Materials

## 目录结构

- `01_data/`：正式冻结数据及人工核验日志
- `02_sources/`：核心来源归档和来源位置注册表
- `03_code/`：可复现的数据处理、QC、冻结与制图代码
- `04_intermediate_results/`：论文复现所需的结构与敏感性中间结果
- `05_figures/`：论文可用PNG和SVG图件
- `06_appendices/`：论文附录和数据来源参考文献材料

## 数据冻结版本

版本：`v1.0`；冻结日期：`2026-08-17`。

## 从RawData重建Final Matrix

以`01_data/raw_benchmark_data_v1.0.csv`中`selected_for_final_modeling=TRUE`的记录为输入，按`model_id × setting_id`透视`raw_score`；列顺序使用`01_data/final_modeling_benchmark_manifest_v1.0.csv`，不得改变原始单位或填补NA。

## 运行QC

在完整项目结构中运行`python 03_code/validate_stage4_freeze.py`。哈希核对使用`01_data/SHA256SUMS_v1.0.txt`。

## 生成论文数据表

运行`python 03_code/stage4_finalize.py`后，再运行`node 03_code/build_stage4_workbooks.mjs`。正式副本已位于`06_appendices/`和`paper_materials/data_section/`。

## Q1默认输入

正式Q1默认读取：`01_data/final_modeling_matrix_v1.0.xlsx`。
