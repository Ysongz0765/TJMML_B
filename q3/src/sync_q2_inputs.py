from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


DEFAULT_SOURCE_BRANCH = "origin/q2-final-paper"
DEFAULT_SYNC_DATE = "2026-08-17"
SOURCE_FILES = {
    "scenario_utility.csv": "q2/outputs/scenario_utility.csv",
    "scenario_utility_bootstrap.csv": "q2/outputs/scenario_utility_bootstrap.csv",
    "scenario_utility_summary.csv": "q2/outputs/scenario_utility_summary.csv",
    "q2_to_q3_validation.csv": "q2/outputs/q2_to_q3_validation.csv",
    "q2_to_q3_interface.md": "q2/metadata/q2_to_q3_interface.md",
}


def _git_show(repo_root: Path, source_branch: str, source_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{source_branch}:{source_path}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sync_q2_inputs(
    repo_root: Path,
    source_branch: str = DEFAULT_SOURCE_BRANCH,
    sync_date: str = DEFAULT_SYNC_DATE,
) -> dict:
    q3_data = repo_root / "q3" / "data"
    q3_data.mkdir(parents=True, exist_ok=True)
    source_commit = subprocess.run(
        ["git", "rev-parse", source_branch],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    records = []
    for target_name, source_path in SOURCE_FILES.items():
        data = _git_show(repo_root, source_branch, source_path)
        target_path = q3_data / target_name
        target_path.write_bytes(data)
        records.append(
            {
                "source_branch": source_branch,
                "source_commit": source_commit,
                "source_path": source_path,
                "target_path": str(target_path.relative_to(repo_root)).replace("\\", "/"),
                "source_sha256": _sha256(data),
                "target_sha256": _sha256(target_path.read_bytes()),
                "sync_date": sync_date,
            }
        )

    provenance = {
        "source_branch": source_branch,
        "source_commit": source_commit,
        "sync_date": sync_date,
        "files": records,
    }
    provenance_path = q3_data / "q2_interface_provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize frozen Q2-to-Q3 interface files from a Git ref.")
    parser.add_argument("--source-branch", default=DEFAULT_SOURCE_BRANCH)
    parser.add_argument("--sync-date", default=DEFAULT_SYNC_DATE)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    provenance = sync_q2_inputs(args.repo_root, args.source_branch, args.sync_date)
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
