from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / "submission_support"
FROZEN = ROOT / "frozen" / "v1.0"
PAPER = ROOT / "paper_materials"


def copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree_files(source: Path, destination: Path, suffixes: set[str] | None = None) -> int:
    count = 0
    for item in source.rglob("*"):
        if not item.is_file() or item.name.endswith(".inspect.ndjson"):
            continue
        if suffixes is not None and item.suffix.lower() not in suffixes:
            continue
        copy_file(item, destination / item.relative_to(source))
        count += 1
    return count


for folder in ["01_data", "02_sources", "03_code", "04_intermediate_results", "05_figures", "06_appendices"]:
    (SUPPORT / folder).mkdir(parents=True, exist_ok=True)

# 01_data: immutable freeze plus the integrated workbook for convenient inspection.
data_count = copy_tree_files(FROZEN, SUPPORT / "01_data")
copy_file(ROOT / "data" / "final" / "LLM_Benchmark_Evaluation_Dataset.xlsx",
          SUPPORT / "01_data" / "LLM_Benchmark_Evaluation_Dataset_v1.0.xlsx")
data_count += 1

# 02_sources: only the archives actually used by the 164 selected records.
selected_source_ids = {"SRC001", "SRC003", "SRC006", "SRC007", "SRC014", "SRC016", "SRC017", "SRC018"}
source_count = 0
for archive in (ROOT / "sources").rglob("*"):
    if not archive.is_file():
        continue
    if any(archive.name.startswith(source_id) for source_id in selected_source_ids):
        copy_file(archive, SUPPORT / "02_sources" / archive.parent.name / archive.name)
        source_count += 1

# The registry workbook was already authored with relative archive locations.
registry = SUPPORT / "02_sources" / "source_location_registry.xlsx"
if not registry.exists():
    copy_file(ROOT / "submission_support" / "02_sources" / "source_location_registry.xlsx", registry)

# 03_code: all scripts needed to reproduce collection, cleaning, audits, freeze and figures.
code_names = [
    "build_dataset.py", "collect_data.py", "clean_data.py", "validate_data.py",
    "conflict_check.py", "coverage_analysis.py", "correlation_analysis.py", "export_results.py",
    "phase2_extend.py", "phase3_modeling_readiness.py", "generate_stage3_paper_figures.py",
    "validate_stage3_outputs.py", "build_stage3_workbooks.mjs", "verify_stage3_workbooks.mjs",
    "stage4_finalize.py", "build_stage4_workbooks.mjs", "stage4_package.py",
    "validate_stage4_freeze.py", "verify_stage4_workbooks.mjs",
]
code_count = 0
for name in code_names:
    source = ROOT / "scripts" / name
    if source.exists():
        copy_file(source, SUPPORT / "03_code" / name)
        code_count += 1

# 04_intermediate_results: model-structure evidence needed to reproduce decisions.
intermediate_names = [
    "benchmark_setting_audit.xlsx", "source_concentration_analysis.xlsx",
    "benchmark_redundancy_audit.xlsx", "pairwise_network_diagnostics.xlsx",
    "spearman_missing_aware.xlsx", "modeling_readiness_gate.xlsx",
    "bt_identifiability_test.xlsx", "final_traceability_report.xlsx",
    "final_modeling_benchmark_manifest.xlsx", "benchmark_family_manifest.xlsx",
]
intermediate_count = 0
for name in intermediate_names:
    source = ROOT / "data" / "processed" / name
    if source.exists():
        copy_file(source, SUPPORT / "04_intermediate_results" / name)
        intermediate_count += 1

# 05_figures: exactly the 21 final Stage 3/4 figure pairs.
figure_count = copy_tree_files(ROOT / "reports" / "figures" / "stage3", SUPPORT / "05_figures", {".png", ".svg"})

# 06_appendices: paper-facing source text, tables, appendices and reference mapping.
appendix_count = 0
for item in PAPER.iterdir():
    if item.is_file() and not item.name.endswith(".inspect.ndjson"):
        copy_file(item, SUPPORT / "06_appendices" / item.name)
        appendix_count += 1
copy_file(ROOT / "reports" / "final_modeling_readiness_certificate.md",
          SUPPORT / "06_appendices" / "final_modeling_readiness_certificate.md")
appendix_count += 1

copy_file(ROOT / "reports" / "ai_tool_usage_record.md", SUPPORT / "ai_tool_usage_record.md")


def scan_text(text: str, relative_path: str) -> list[dict[str, str]]:
    rules = {
        "windows_absolute_path": re.compile(r"(?i)\b[A-Z]:\\(?:Users|study|Documents|Desktop|Downloads)\\"),
        "user_profile_path": re.compile(r"(?i)C:\\Users\\[^\\\s]+"),
        "file_uri": re.compile(r"(?i)file:///"),
        "unix_user_path": re.compile(r"(?i)/Users/[^/\s]+|/home/[^/\s]+"),
    }
    findings = []
    for rule_name, pattern in rules.items():
        for match in pattern.finditer(text):
            findings.append({"file": relative_path, "rule": rule_name, "match": match.group(0)[:120]})
    return findings


def scan_package() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    text_suffixes = {".md", ".txt", ".csv", ".json", ".py", ".mjs", ".xml"}
    for file_path in SUPPORT.rglob("*"):
        if not file_path.is_file() or file_path.name == "anonymity_scan_report.md":
            continue
        relative = file_path.relative_to(SUPPORT).as_posix()
        # The scanner source contains the path patterns as regex literals; inspect it through code review,
        # not by matching those literals against themselves.
        if relative == "03_code/stage4_package.py":
            continue
        # Public source archives contain publisher identities; only scan our formal registry in 02_sources.
        if relative.startswith("02_sources/") and file_path.name != "source_location_registry.xlsx":
            continue
        if file_path.suffix.lower() in text_suffixes:
            findings.extend(scan_text(file_path.read_text(encoding="utf-8", errors="ignore"), relative))
        elif file_path.suffix.lower() == ".xlsx":
            with zipfile.ZipFile(file_path) as workbook_zip:
                for member in workbook_zip.namelist():
                    if member.endswith(".xml") or member.endswith(".rels"):
                        text = workbook_zip.read(member).decode("utf-8", errors="ignore")
                        findings.extend(scan_text(text, f"{relative}!{member}"))
    return findings


findings = scan_package()
scan_status = "PASS" if not findings else "REVIEW_REQUIRED"
report_lines = [
    "# Anonymity Scan Report",
    "",
    "- Scope: submission_support formal data, code, intermediate results, figures, appendices and registries",
    "- Exclusion: archived public source page contents are excluded because publisher/author identities are source evidence, not team identity",
    "- Scanner self-check: 03_code/stage4_package.py is excluded from regex self-matching; it contains only project-relative paths",
    "- Rules: local absolute paths, user-profile paths, file URIs and Unix home paths",
    f"- Result: `{scan_status}`",
    f"- Findings: {len(findings)}",
    "",
]
if findings:
    report_lines.extend(["| File | Rule | Match |", "|---|---|---|"])
    report_lines.extend(f"| {x['file']} | {x['rule']} | `{x['match']}` |" for x in findings)
else:
    report_lines.append("No participant-identifying local path or user-profile leakage was detected in the formal package.")
report_lines.extend([
    "",
    "This is an automated anonymity scan. Competition identifiers, author names and institution fields should still be checked against the contest's submission rules before upload.",
])
(SUPPORT / "anonymity_scan_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

package_manifest = {
    "freeze_version": "v1.0",
    "freeze_date": "2026-08-17",
    "data_files": data_count,
    "source_archives": source_count,
    "code_files": code_count,
    "intermediate_files": intermediate_count,
    "figure_files": figure_count,
    "appendix_files": appendix_count,
    "anonymity_scan": scan_status,
}
(SUPPORT / "package_manifest.json").write_text(json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

zip_base = ROOT / "submission_support_v1.0"
archive = Path(shutil.make_archive(str(zip_base), "zip", root_dir=ROOT, base_dir="submission_support"))
print(json.dumps({**package_manifest, "archive": str(archive)}, ensure_ascii=False, indent=2))
