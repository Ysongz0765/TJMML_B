from build_dataset import ROOT, core_selection, correlation, make_dataframes, matrix_and_standardized, select_records


def main() -> None:
    dfs = make_dataframes()
    core = core_selection(dfs["RawData"], dfs["Models"])
    selected = select_records(dfs["RawData"], core)
    matrix, _ = matrix_and_standardized(dfs["Models"], selected)
    corr, n = correlation(matrix)
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out / "benchmark_spearman_matrix.xlsx", engine="openpyxl") as writer:
        corr.to_excel(writer, sheet_name="spearman")
        n.to_excel(writer, sheet_name="pairwise_sample_size_matrix")
    print("Wrote Spearman and pairwise sample-size matrices.")


if __name__ == "__main__":
    main()
