from build_dataset import ROOT, make_dataframes
import pandas as pd


def main() -> None:
    dfs = make_dataframes()
    out = ROOT / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    dfs["CandidateModels"].to_csv(out / "candidate_models.csv", index=False, encoding="utf-8-sig")
    dfs["RawData"].to_csv(out / "raw_benchmark_data.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(out / "raw_benchmark_data.xlsx", engine="openpyxl") as writer:
        dfs["RawData"].to_excel(writer, index=False, sheet_name="RawData")
    print(f"Collected {len(dfs['RawData'])} raw benchmark records.")


if __name__ == "__main__":
    main()
