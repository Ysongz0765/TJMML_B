from build_dataset import ROOT, conflict_check, make_dataframes


def main() -> None:
    dfs = make_dataframes()
    conflicts = conflict_check(dfs["RawData"])
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    conflicts.to_excel(out / "data_conflicts.xlsx", index=False)
    print(f"Detected {len(conflicts)} conflicts.")


if __name__ == "__main__":
    main()
