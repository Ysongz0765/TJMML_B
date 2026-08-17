from build_dataset import ROOT, conflict_check, core_selection, make_dataframes, matrix_and_standardized, qc_sheet, select_records


def main() -> None:
    dfs = make_dataframes()
    conflicts = conflict_check(dfs["RawData"])
    core = core_selection(dfs["RawData"], dfs["Models"])
    selected = select_records(dfs["RawData"], core)
    matrix, _ = matrix_and_standardized(dfs["Models"], selected)
    qc = qc_sheet(dfs["RawData"], dfs["Models"], dfs["Benchmarks"], conflicts, matrix)
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    qc.to_excel(out / "qc_checks.xlsx", index=False)
    failed = qc[qc["status"].eq("FAIL")]
    if not failed.empty:
        raise SystemExit(f"QC failed:\n{failed.to_string(index=False)}")
    print("QC checks passed.")


if __name__ == "__main__":
    main()
