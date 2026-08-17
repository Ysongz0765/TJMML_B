from build_dataset import ROOT, coverage, make_dataframes
import pandas as pd


def main() -> None:
    dfs = make_dataframes()
    bench_cov, model_cov = coverage(dfs["RawData"], dfs["Models"])
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out / "benchmark_coverage.xlsx", engine="openpyxl") as writer:
        bench_cov.to_excel(writer, index=False, sheet_name="benchmark_coverage")
        model_cov.to_excel(writer, index=False, sheet_name="model_coverage")
    print(f"Wrote coverage for {len(bench_cov)} benchmark settings and {len(model_cov)} models.")


if __name__ == "__main__":
    main()
