"""Generate data-backed supplementary tables for the integrated paper."""

from __future__ import annotations

from pathlib import Path
import math

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_final" / "sections" / "10_appendix.tex"

SHORT_MODEL = {
    "kimi_k3_max": "Kimi K3",
    "gpt_5_6_sol_max": "GPT-5.6 Sol",
    "gpt_5_5_xhigh": "GPT-5.5",
    "claude_fable_5_max": "Claude Fable 5",
    "claude_opus_4_8_max": "Claude Opus 4.8",
    "gemini_3_1_pro_high": "Gemini-3.1-Pro",
    "deepseek_v4_pro_max": "DeepSeek-V4-Pro",
    "deepseek_v4_flash_max": "DeepSeek-V4-Flash",
    "qwen3_8_max": "Qwen3.8-Max",
    "glm_5_2_max": "GLM-5.2",
}


def tex(value: object) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def num(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "--"
    return f"{float(value):.{digits}f}"


def rank(value: object) -> str:
    if pd.isna(value):
        return "--"
    return str(int(value))


def build_loso() -> str:
    path = ROOT / "outputs" / "q1_v1.2" / "tables" / "table_q1_v12_loso.xlsx"
    df = pd.read_excel(path, sheet_name="Scenario_Summary")
    rows = []
    for _, row in df.iterrows():
        if str(row["status"]) == "NETWORK_DISCONNECTED":
            rows.append(
                f"{tex(row['removed'])} & $\\times$ & -- & -- & -- & -- \\\\"
            )
        else:
            rows.append(
                f"{tex(row['removed'])} & {int(row['common_models'])} & "
                f"{num(row['spearman'])} & {rank(row['kimi_rank_other'])} & "
                f"{int(row['top3_overlap_count'])} & OK \\\\"
            )
    return "\n".join(rows)


def build_equal_weight() -> str:
    path = ROOT / "outputs" / "q1_v1.2" / "tables" / "table_q1_v12_equal_weight_sensitivity.xlsx"
    df = pd.read_excel(path, sheet_name="Ranking_A")
    df = df.sort_values("main_rank")
    rows = []
    for _, row in df.iterrows():
        change = int(row["rank_change"])
        change_text = f"{change:+d}" if change else "0"
        rows.append(
            f"{rank(row['main_rank'])} & {tex(SHORT_MODEL.get(row['model_id'], row['model']))} & "
            f"{rank(row['equal_weight_rank'])} & {change_text} & "
            f"{num(row['main_score'], 1)} & {num(row['equal_weight_score'], 1)} \\\\"
        )
    return "\n".join(rows)


def build_pricing() -> str:
    path = ROOT / "q3" / "frozen" / "v1.0" / "model_pricing.csv"
    df = pd.read_csv(path, keep_default_na=False)
    rows = []
    for _, row in df.iterrows():
        source = row["source_url"]
        source_link = rf"\href{{{source}}}{{official}}"
        config = f"{row['exact_version']} / {row['api_model']}"
        rows.append(
            f"{tex(row['model_name'])} & {tex(row['price_date'])} & "
            f"{tex(config)} & {source_link} \\\\"
        )
    return "\n".join(rows)


def main() -> None:
    content = rf"""\appendix
\section{{补充稳健性与价格快照}}

\subsection{{LOSO 稳健性}}
LOSO 结果直接读取 Q1 正式输出。有效比较保留共同模型数、与完整 Ranking A 的 Spearman 相关、Kimi 的其他排名和前三重叠数；比较网络断开时以 $\times$ 标记，不将其填充为数值。

\begin{{table}}[htbp]
\centering
\caption{{LOSO 场景/来源删除审计。数据源：\texttt{{outputs/q1\_v1.2/tables/table\_q1\_v12\_loso.xlsx}}，sheet \texttt{{Scenario\_Summary}}。}}
\label{{tab:loso}}
\small
\begin{{tabularx}}{{\textwidth}}{{lrrrrl}}
\toprule
删除对象 & Common-N & Spearman & Kimi 其他排名 & Top-3 重叠 & 状态\\
\midrule
{build_loso()}
\bottomrule
\end{{tabularx}}
\end{{table}}

\subsection{{等权敏感性}}
将 Q1 综合权重替换为五维等权后，Ranking A 前三模型及其顺序保持不变；完整十模型的名次变化见表~\ref{{tab:equalweight}}。该表只报告正式等权敏感性输出，不重新估计任何分数。

\begin{{table}}[htbp]
\centering
\caption{{等权敏感性的逐模型比较。}}
\label{{tab:equalweight}}
\small
\begin{{tabularx}}{{\textwidth}}{{rXrrrr}}
\toprule
完整排名 & 模型 & 等权排名 & 名次变化 & 原得分 & 等权得分\\
\midrule
{build_equal_weight()}
\bottomrule
\end{{tabularx}}
\end{{table}}

\subsection{{动态价格记录}}
价格只用于 Q3 成本审计，冻结快照日期、API SKU、评测配置和供应商官方来源均保留在表~\ref{{tab:pricing_snapshot}}。其中 \texttt{{SPECIAL\_CASE}} 和缺失价格不会被视为零成本，也不进入严格 FULL 主 Pareto。

\begin{{table}}[htbp]
\centering
\caption{{Q3 动态价格快照与 SKU/configuration 记录。数据源：\texttt{{q3/frozen/v1.0/model\_pricing.csv}}；price\_date 为冻结/快照日期。}}
\label{{tab:pricing_snapshot}}
\scriptsize
\begin{{tabularx}}{{\textwidth}}{{p{{3.0cm}}p{{1.6cm}}p{{6.0cm}}X}}
\toprule
模型 & 快照日期 & SKU / exact configuration & 官方来源\\
\midrule
{build_pricing()}
\bottomrule
\end{{tabularx}}
\end{{table}}
"""
    OUT.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
