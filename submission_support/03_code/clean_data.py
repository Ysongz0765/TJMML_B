from build_dataset import ROOT, make_dataframes
import pandas as pd


def main() -> None:
    dfs = make_dataframes()
    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    raw = dfs["RawData"].copy()
    raw["numeric_score"] = pd.to_numeric(raw["raw_score"], errors="coerce")
    raw["benchmark_setting_key"] = raw.apply(
        lambda r: f"{r['benchmark_name']}|{r['benchmark_version']}|{r['metric_name']}|tools={r['tools_allowed']}|reasoning={r['reasoning_setting']}",
        axis=1,
    )
    raw.to_csv(processed / "processed_benchmark_data.csv", index=False, encoding="utf-8-sig")
    raw.to_excel(processed / "processed_benchmark_data.xlsx", index=False)
    print(f"Cleaned {len(raw)} records.")


if __name__ == "__main__":
    main()
