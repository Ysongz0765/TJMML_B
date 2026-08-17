import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const bundlePath = path.join(root, "data", "processed", "stage3_analysis_bundle.json");
const bundle = JSON.parse(await fs.readFile(bundlePath, "utf8"));
const { tables, columns, metadata } = bundle;
const mirrorDir = path.join(root, "outputs", "stage3_llm_benchmark");
await fs.mkdir(mirrorDir, { recursive: true });

function colName(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    n -= 1;
    out = String.fromCharCode(65 + (n % 26)) + out;
    n = Math.floor(n / 26);
  }
  return out;
}

function tableMatrix(tableName, nullAsNA = false) {
  const headers = columns[tableName];
  const rows = tables[tableName].map((row) => headers.map((header) => {
    const value = row[header];
    if (value === null || value === undefined) return nullAsNA ? "NA" : null;
    return value;
  }));
  return [headers, ...rows];
}

function styleSheet(sheet, matrix, { statusColumns = [], validationStatus = false } = {}) {
  const rowCount = matrix.length;
  const colCount = matrix[0]?.length || 1;
  const end = `${colName(colCount - 1)}${Math.max(1, rowCount)}`;
  const used = sheet.getRange(`A1:${end}`);
  sheet.showGridLines = false;
  used.format.font = { name: "Aptos", size: 9, color: "#1F2933" };
  used.format.verticalAlignment = "center";
  const header = sheet.getRange(`A1:${colName(colCount - 1)}1`);
  header.format.fill = "#1F4E78";
  header.format.font = { name: "Aptos Display", size: 10, bold: true, color: "#FFFFFF" };
  header.format.rowHeight = 28;
  header.format.wrapText = true;
  header.format.borders = { bottom: { style: "medium", color: "#17365D" } };
  if (rowCount > 1) {
    const body = sheet.getRange(`A2:${end}`);
    body.format.borders = { insideHorizontal: { style: "thin", color: "#E3E8EC" } };
  }
  for (let c = 0; c < colCount; c += 1) {
    const textLengths = matrix.slice(0, Math.min(rowCount, 250)).map((row) => String(row[c] ?? "").length);
    const maxLen = Math.max(...textLengths, 8);
    const width = Math.min(46, Math.max(10, Math.ceil(maxLen * 0.92)));
    const range = sheet.getRangeByIndexes(0, c, rowCount, 1);
    range.format.columnWidth = width;
    if (maxLen > 48) {
      range.format.wrapText = true;
    }
    const headerText = String(matrix[0]?.[c] ?? "").toLowerCase();
    if (/coverage|share|rate|rho|p_value|hhi|ratio|score|difference|weight/.test(headerText)) {
      if (rowCount > 1) sheet.getRangeByIndexes(1, c, rowCount - 1, 1).setNumberFormat("0.000");
    }
  }
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(Math.min(4, colCount));
  const headerMap = new Map(matrix[0].map((value, index) => [String(value), index]));
  for (const statusColumn of statusColumns) {
    const c = headerMap.get(statusColumn);
    if (c === undefined) continue;
    for (let r = 1; r < rowCount; r += 1) {
      const value = String(matrix[r][c] ?? "").toUpperCase();
      const cell = sheet.getCell(r, c);
      if (value === "TRUE" || value.includes("PASS") || value.includes("READY") || value === "OK" || value === "VERIFIED") {
        cell.format.fill = "#E2F0D9";
        cell.format.font = { color: "#276221", bold: true };
      } else if (value === "FALSE" || value.includes("FAIL") || value.includes("HIGH") || value.includes("PENDING")) {
        cell.format.fill = "#FCE4D6";
        cell.format.font = { color: "#9C2F1B", bold: true };
      }
    }
  }
  if (validationStatus && headerMap.has("checkbox_status") && rowCount > 1) {
    const c = headerMap.get("checkbox_status");
    sheet.getRangeByIndexes(1, c, rowCount - 1, 1).dataValidation = {
      rule: { type: "list", values: ["PENDING", "VERIFIED", "MISMATCH", "NOT_APPLICABLE"] },
    };
  }
}

function writeTable(workbook, sheetName, tableName, options = {}) {
  const sheet = workbook.worksheets.getOrAdd(sheetName, { renameFirstIfOnlyNewSpreadsheet: true });
  sheet.deleteAllDrawings();
  const old = sheet.getUsedRange();
  if (old) old.clear({ applyTo: "all" });
  const matrix = tableMatrix(tableName, options.nullAsNA ?? false);
  sheet.getRangeByIndexes(0, 0, matrix.length, matrix[0].length).values = matrix;
  styleSheet(sheet, matrix, options);
  return sheet;
}

function writeReadme(workbook, title, notes = []) {
  const rows = [
    ["Item", "Value"],
    ["Artifact", title],
    ["Generated / access date", metadata.generated_at],
    ["Readiness status", metadata.status],
    ["Core models", metadata.core_models],
    ["Exact settings", metadata.exact_settings],
    ["Benchmark families", metadata.benchmark_families],
    ["Raw records", metadata.raw_records],
    ["Selected matrix cells", metadata.selected_cells],
    ["Overall coverage", metadata.coverage],
    ["Human-verified cells", metadata.human_verified_cells],
    ["Missing-value rule", "NA is retained; no imputation or AI-estimated score."],
    ["Weighting rule", "Equal capability weight; equal family weight inside capability; settings divide family weight."],
    ["Traceability", "Every nonempty final-matrix cell maps to record_id, source_id, URL and archived location."],
    ...notes.map((note, index) => [`Note ${index + 1}`, note]),
  ];
  const sheet = workbook.worksheets.getOrAdd("README", { renameFirstIfOnlyNewSpreadsheet: true });
  sheet.getRangeByIndexes(0, 0, rows.length, 2).values = rows;
  styleSheet(sheet, rows, { statusColumns: ["Value"] });
  sheet.getRange("A1:B1").format.fill = "#17365D";
  sheet.getRange("A1:B1").format.font = { name: "Aptos Display", size: 11, bold: true, color: "#FFFFFF" };
  sheet.getRange("A1:A40").format.columnWidth = 26;
  sheet.getRange("B1:B40").format.columnWidth = 72;
  sheet.getRange("B1:B40").format.wrapText = true;
  return sheet;
}

async function saveWorkbook(workbook, outputPath, mirror = true) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(outputPath);
  if (mirror) await blob.save(path.join(mirrorDir, path.basename(outputPath)));
}

const specifications = [
  { file: "data/final/final_modeling_matrix.xlsx", title: "Final Modeling Matrix", sheets: [
    ["Matrix", "FinalModelingMatrix", { nullAsNA: true }], ["Standardized", "StandardizedMatrix", { nullAsNA: true }], ["Lineage", "Lineage", {}],
  ], notes: ["This workbook is the sole default input for formal modeling after human sign-off."] },
  { file: "data/processed/final_modeling_benchmark_manifest.xlsx", title: "Final Modeling Benchmark Manifest", sheets: [["Manifest", "ModelingBenchmarkManifest", {}]] },
  { file: "data/processed/benchmark_family_manifest.xlsx", title: "Benchmark Family Manifest", sheets: [["BenchmarkFamilies", "BenchmarkFamilies", {}]] },
  { file: "data/processed/livebench_independence_audit.xlsx", title: "LiveBench Independence Audit", sheets: [["LiveBenchAudit", "LiveBenchAudit", {}]] },
  { file: "data/processed/source_concentration_analysis.xlsx", title: "Source Concentration Analysis", sheets: [["Summary", "SourceConcentrationSummary", { statusColumns: ["dominance_flag"] }], ["Detail", "SourceConcentration", {}]] },
  { file: "data/processed/leave_one_source_out_diagnostics.xlsx", title: "Leave-One-Source-Out Diagnostics", sheets: [["Diagnostics", "LeaveOneSourceOut", { statusColumns: ["source_dependence_flag"] }]] },
  { file: "data/processed/bridge_evidence_report.xlsx", title: "Bridge Evidence Report", sheets: [["BridgeEvidence", "BridgeEvidence", { statusColumns: ["risk", "cross_validation_status"] }]] },
  { file: "data/processed/kimi_evidence_audit.xlsx", title: "Kimi K3 Evidence Audit", sheets: [["KimiAudit", "KimiAudit", { statusColumns: ["single_source_risk"] }]] },
  { file: "data/processed/benchmark_redundancy_audit.xlsx", title: "Benchmark Redundancy Audit", sheets: [["RedundancyAudit", "RedundancyAudit", { statusColumns: ["audit_result", "redundancy_risk"] }]] },
  { file: "data/processed/spearman_missing_aware.xlsx", title: "Missing-Aware Spearman Analysis", sheets: [
    ["Rho", "SpearmanRho", { nullAsNA: true }], ["PValue", "SpearmanPValue", { nullAsNA: true }],
    ["PairwiseN", "SpearmanN", { nullAsNA: true }], ["Overlap", "SpearmanOverlap", { nullAsNA: true }], ["PairwiseLong", "SpearmanLong", { nullAsNA: true }],
  ], notes: ["Pairs with fewer than six shared models are exploratory; n=2-3 is never described as reliable correlation."] },
  { file: "data/processed/family_effect_sensitivity.xlsx", title: "Benchmark Family Effect Sensitivity", sheets: [["Sensitivity", "FamilySensitivity", {}], ["FamilySpearman", "FamilySpearman", { nullAsNA: true }]] },
  { file: "data/processed/bt_identifiability_test.xlsx", title: "Bradley-Terry Identifiability Test", sheets: [["BTReadiness", "BTReadiness", { statusColumns: ["readiness", "separation_warning"] }], ["NetworkQC", "NetworkQC", { statusColumns: ["scope_note"] }]] },
  { file: "data/processed/livebench_dependency_sensitivity.xlsx", title: "LiveBench Dependency Sensitivity", sheets: [["LiveBenchDependency", "LiveBenchDependency", { statusColumns: ["interpretation"] }]] },
  { file: "data/processed/human_verification_final_checklist.xlsx", title: "Human Verification Final Checklist", sheets: [["Checklist", "HumanVerification", { statusColumns: ["checkbox_status"], validationStatus: true }]], notes: ["Codex did not set any human verification field to TRUE."] },
  { file: "data/processed/modeling_readiness_gate.xlsx", title: "Modeling Readiness Gate", sheets: [["Gate", "ModelingReadinessGate", { statusColumns: ["passed", "overall_status"] }], ["NetworkQC", "NetworkQC", {}]] },
];

for (const spec of specifications) {
  const workbook = Workbook.create();
  writeReadme(workbook, spec.title, spec.notes ?? []);
  for (const [sheetName, tableName, options] of spec.sheets) writeTable(workbook, sheetName, tableName, options);
  await saveWorkbook(workbook, path.join(root, spec.file));
}

for (const [file, tableName, sheetName] of [
  ["data/raw/raw_benchmark_data.xlsx", "RawData", "RawData"],
  ["data/processed/source_registry.xlsx", "Sources", "Sources"],
]) {
  const workbook = Workbook.create();
  writeTable(workbook, sheetName, tableName, {});
  await saveWorkbook(workbook, path.join(root, file));
}

const totalPath = path.join(root, "data", "final", "LLM_Benchmark_Evaluation_Dataset.xlsx");
const total = await SpreadsheetFile.importXlsx(await FileBlob.load(totalPath));
writeReadme(total, "LLM Benchmark Evaluation Dataset - Phase 3", [
  "The FinalModelingMatrix sheet is the sole default modeling input; the Phase 2 Matrix remains for historical audit.",
  "Final status is pending human sign-off because no human verification override file was present.",
]);
const modelsSheet = total.worksheets.getItem("Models");
modelsSheet.getRange("I11:K11").values = [[
  "BRIDGE_MODEL",
  "Retained as historical Qwen bridge evidence; Qwen3.8-Max is the current core Qwen representative.",
  "Not used as a core row in FinalModelingMatrix.",
]];
modelsSheet.getRange("I15:K15").values = [[
  "CORE_MODEL",
  "Current representative Alibaba/Qwen version with unified LiveBench plus Phase 3 HLE, AA-LCR and MMMU-Pro evidence.",
  "Exact-setting coverage meets the Phase 3 core-model gate; human verification remains pending.",
]];
writeTable(total, "RawData", "RawData", {});
writeTable(total, "Sources", "Sources", {});
for (const [sheetName, tableName, options] of [
  ["FinalModelingMatrix", "FinalModelingMatrix", { nullAsNA: true }],
  ["ModelingBenchmarkManifest", "ModelingBenchmarkManifest", {}],
  ["BenchmarkFamilies", "BenchmarkFamilies", {}],
  ["LiveBenchAudit", "LiveBenchAudit", {}],
  ["SourceConcentration", "SourceConcentrationSummary", { statusColumns: ["dominance_flag"] }],
  ["BridgeEvidence", "BridgeEvidence", {}],
  ["KimiAudit", "KimiAudit", {}],
  ["RedundancyAudit", "RedundancyAudit", {}],
  ["SpearmanQC", "SpearmanLong", { nullAsNA: true }],
  ["BTReadiness", "BTReadiness", { statusColumns: ["readiness", "separation_warning"] }],
  ["ModelingReadinessGate", "ModelingReadinessGate", { statusColumns: ["passed", "overall_status"] }],
]) writeTable(total, sheetName, tableName, options);
await saveWorkbook(total, totalPath);

console.log(JSON.stringify({
  workbooks: specifications.length + 3,
  totalWorkbook: totalPath,
  mirrorDir,
  status: metadata.status,
}));
