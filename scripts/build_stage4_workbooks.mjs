import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const bundlePath = path.join(root, "data", "processed", "stage4_finalization_bundle.json");
const bundle = JSON.parse(await fs.readFile(bundlePath, "utf8"));
const { tables, columns, metadata } = bundle;
const frozenDir = path.join(root, "frozen", "v1.0");
const mirrorDir = path.join(root, "outputs", "stage4_final");
await fs.mkdir(frozenDir, { recursive: true });
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

function styleSheet(sheet, matrix, { statusColumns = [], bodyRowHeight = null } = {}) {
  const rowCount = matrix.length;
  const colCount = matrix[0]?.length || 1;
  const lastCol = colName(colCount - 1);
  const used = sheet.getRange(`A1:${lastCol}${Math.max(1, rowCount)}`);
  sheet.showGridLines = false;
  used.format.font = { name: "Aptos", size: 9, color: "#1F2933" };
  used.format.verticalAlignment = "center";
  const header = sheet.getRange(`A1:${lastCol}1`);
  header.format.fill = "#1F4E78";
  header.format.font = { name: "Aptos Display", size: 10, bold: true, color: "#FFFFFF" };
  header.format.rowHeight = 46;
  header.format.wrapText = true;
  header.format.borders = { bottom: { style: "medium", color: "#17365D" } };
  if (rowCount > 1) {
    const body = used.getRangeByIndexes(1, 0, rowCount - 1, colCount);
    body.format.borders = {
      insideHorizontal: { style: "thin", color: "#E3E8EC" },
    };
    if (bodyRowHeight !== null) body.format.rowHeight = bodyRowHeight;
  }
  for (let c = 0; c < colCount; c += 1) {
    const lengths = matrix.slice(0, Math.min(rowCount, 260)).map((row) => String(row[c] ?? "").length);
    const maxLen = Math.max(...lengths, 8);
    const width = Math.min(48, Math.max(10, Math.ceil(maxLen * 0.9)));
    const column = sheet.getRangeByIndexes(0, c, rowCount, 1);
    column.format.columnWidth = width;
    if (maxLen > 45) column.format.wrapText = true;
    const label = String(matrix[0]?.[c] ?? "").toLowerCase();
    if (/coverage|share|rate|rho|p_value|hhi|ratio|score|difference|weight/.test(label) && rowCount > 1) {
      sheet.getRangeByIndexes(1, c, rowCount - 1, 1).setNumberFormat("0.000");
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
      if (value === "TRUE" || value.includes("PASS") || value.includes("READY") || value === "OK" || value === "VERIFIED" || value === "FROZEN") {
        cell.format.fill = "#E2F0D9";
        cell.format.font = { color: "#276221", bold: true };
      } else if (value === "FALSE" || value.includes("FAIL") || value.includes("PENDING") || value.includes("REVIEW")) {
        cell.format.fill = "#FCE4D6";
        cell.format.font = { color: "#9C2F1B", bold: true };
      }
    }
  }
}

function writeMatrix(sheet, matrix, options = {}) {
  sheet.deleteAllDrawings();
  const old = sheet.getUsedRange();
  if (old) old.clear({ applyTo: "all" });
  sheet.getRangeByIndexes(0, 0, matrix.length, matrix[0].length).values = matrix;
  styleSheet(sheet, matrix, options);
}

function writeTable(workbook, sheetName, tableName, options = {}) {
  const sheet = workbook.worksheets.getOrAdd(sheetName, { renameFirstIfOnlyNewSpreadsheet: true });
  writeMatrix(sheet, tableMatrix(tableName, options.nullAsNA ?? false), options);
  return sheet;
}

function readmeRows(title, notes = []) {
  return [
    ["Item", "Value"],
    ["Artifact", title],
    ["Dataset status", metadata.status],
    ["Freeze version", metadata.data_freeze_version],
    ["Freeze date", metadata.data_freeze_date],
    ["Core models", metadata.core_models],
    ["Exact benchmark settings", metadata.exact_settings],
    ["Benchmark families", metadata.benchmark_families],
    ["Raw records", metadata.raw_records],
    ["Selected matrix cells", metadata.selected_cells],
    ["Overall coverage", metadata.coverage],
    ["Human-verified selected cells", metadata.human_verified_cells],
    ["Traceability rate", metadata.traceability_rate],
    ["Missing values", "NA is retained. No imputation, interpolation or AI-estimated score is used."],
    ["Verification provenance", "The competition team completed manual verification before Stage 4; Stage 4 records that status only."],
    ["Modeling input", "Use FinalModelingMatrix / final_modeling_matrix_v1.0.xlsx as the sole default Q1 input."],
    ...notes.map((note, index) => [`Note ${index + 1}`, note]),
  ];
}

function writeReadme(workbook, title, notes = []) {
  const sheet = workbook.worksheets.getOrAdd("README", { renameFirstIfOnlyNewSpreadsheet: true });
  const rows = readmeRows(title, notes);
  writeMatrix(sheet, rows, { statusColumns: ["Value"] });
  sheet.getRange("A1:B1").format.fill = "#17365D";
  sheet.getRange("A1:B1").format.font = { name: "Aptos Display", size: 11, bold: true, color: "#FFFFFF" };
  sheet.getRange(`A1:A${rows.length}`).format.columnWidth = 31;
  sheet.getRange(`B1:B${rows.length}`).format.columnWidth = 78;
  sheet.getRange(`B1:B${rows.length}`).format.wrapText = true;
}

async function saveWorkbook(workbook, outputPath, mirror = true) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(outputPath);
  if (mirror) await blob.save(path.join(mirrorDir, path.basename(outputPath)));
}

async function createWorkbook(outputPath, title, specs, notes = []) {
  const workbook = Workbook.create();
  writeReadme(workbook, title, notes);
  for (const [sheetName, tableName, options = {}] of specs) writeTable(workbook, sheetName, tableName, options);
  await saveWorkbook(workbook, outputPath);
}

const ordinarySpecs = [
  ["data/raw/raw_benchmark_data.xlsx", "Raw Benchmark Data - Stage 4", [["RawData", "RawData", { statusColumns: ["human_verified", "verification_status"] }]]],
  ["data/processed/human_verification_final_checklist.xlsx", "Human Verification Final Checklist", [["Checklist", "HumanVerification", { statusColumns: ["human_verified", "checkbox_status"], bodyRowHeight: 42 }]]],
  ["data/processed/modeling_readiness_gate.xlsx", "Modeling Readiness Gate - Stage 4", [["Gate", "ModelingReadinessGate", { statusColumns: ["passed", "overall_status"] }], ["NetworkQC", "NetworkQC", {}]]],
  ["data/processed/final_traceability_report.xlsx", "Final Traceability Report", [["Traceability", "FinalTraceability", { statusColumns: ["traceability_pass", "human_verified"], bodyRowHeight: 42 }]]],
  ["paper_materials/paper_table_data_sources.xlsx", "Paper Table - Data Sources", [["DataSources", "PaperDataSources", {}]]],
  ["paper_materials/appendix_A_benchmark_system.xlsx", "Appendix A - Benchmark System", [["AppendixA", "AppendixA", {}]]],
  ["paper_materials/appendix_B_source_mapping.xlsx", "Appendix B - Source Mapping", [["AppendixB", "AppendixB", {}]]],
  ["paper_materials/source_reference_mapping.xlsx", "Source Reference Mapping", [["References", "SourceReferenceMapping", {}]]],
  ["paper_materials/appendix_C_model_versions.xlsx", "Appendix C - Model Versions", [["AppendixC", "AppendixC", {}]]],
  ["submission_support/02_sources/source_location_registry.xlsx", "Source Location Registry", [["Locations", "SourceLocationRegistry", {}]]],
  ["paper_materials/data_section/data_source_table.xlsx", "Data Source Table", [["DataSources", "PaperDataSources", {}]]],
  ["paper_materials/data_section/benchmark_system_table.xlsx", "Benchmark System Table", [["Benchmarks", "AppendixA", {}]]],
  ["paper_materials/data_section/model_versions_table.xlsx", "Model Versions Table", [["Models", "AppendixC", {}]]],
  ["paper_materials/data_section/source_mapping_table.xlsx", "Source Mapping Table", [["Sources", "AppendixB", {}]]],
];

for (const [relativePath, title, specs] of ordinarySpecs) {
  await createWorkbook(path.join(root, relativePath), title, specs);
}

const finalMatrixPath = path.join(root, "data", "final", "final_modeling_matrix.xlsx");
await createWorkbook(finalMatrixPath, "Final Modeling Matrix - Fully Verified", [
  ["Matrix", "FinalModelingMatrix", { nullAsNA: true }],
  ["Standardized", "StandardizedMatrix", { nullAsNA: true }],
  ["Lineage", "Lineage", {}],
  ["VerificationLog", "HumanVerificationLog", { statusColumns: ["human_verified", "verification_status"], bodyRowHeight: 42 }],
], ["All 164 nonempty cells were reported as manually verified by the competition team before Stage 4."]);

const totalPath = path.join(root, "data", "final", "LLM_Benchmark_Evaluation_Dataset.xlsx");
const total = await SpreadsheetFile.importXlsx(await FileBlob.load(totalPath));
writeReadme(total, "LLM Benchmark Evaluation Dataset - Frozen v1.0", [
  "All 164 nonempty final-matrix cells are recorded as manually verified by the competition team.",
  "This workbook is frozen for formal mathematical modeling; SHA-256 hashes are stored in frozen/v1.0.",
]);
const modelsSheet = total.worksheets.getItem("Models");
modelsSheet.getRange("I15:K15").values = [[
  "CORE_MODEL",
  "Current representative Alibaba/Qwen version with unified LiveBench plus HLE, AA-LCR and MMMU-Pro evidence.",
  "Exact-setting coverage, traceability and team manual-verification gates passed in frozen v1.0.",
]];
for (const [sheetName, tableName, options] of [
  ["RawData", "RawData", { statusColumns: ["human_verified", "verification_status"] }],
  ["Sources", "Sources", {}],
  ["FinalModelingMatrix", "FinalModelingMatrix", { nullAsNA: true }],
  ["StandardizedMatrix", "StandardizedMatrix", { nullAsNA: true }],
  ["ModelingBenchmarkManifest", "ModelingBenchmarkManifest", {}],
  ["BenchmarkFamilies", "BenchmarkFamilies", {}],
  ["HumanVerificationLog", "HumanVerificationLog", { statusColumns: ["human_verified", "verification_status"], bodyRowHeight: 42 }],
  ["FinalTraceability", "FinalTraceability", { statusColumns: ["traceability_pass", "human_verified"], bodyRowHeight: 42 }],
  ["ModelingReadinessGate", "ModelingReadinessGate", { statusColumns: ["passed", "overall_status"] }],
]) writeTable(total, sheetName, tableName, options);
await saveWorkbook(total, totalPath);

const frozenSpecs = [
  ["final_modeling_matrix_v1.0.xlsx", "Frozen Final Modeling Matrix v1.0", [["Matrix", "FinalModelingMatrix", { nullAsNA: true }], ["Standardized", "StandardizedMatrix", { nullAsNA: true }], ["Lineage", "Lineage", {}]]],
  ["raw_benchmark_data_v1.0.xlsx", "Frozen Raw Benchmark Data v1.0", [["RawData", "RawData", { statusColumns: ["human_verified", "verification_status"] }]]],
  ["source_registry_v1.0.xlsx", "Frozen Source Registry v1.0", [["Sources", "Sources", {}]]],
  ["final_modeling_benchmark_manifest_v1.0.xlsx", "Frozen Final Modeling Benchmark Manifest v1.0", [["Manifest", "ModelingBenchmarkManifest", {}]]],
  ["benchmark_family_manifest_v1.0.xlsx", "Frozen Benchmark Family Manifest v1.0", [["Families", "BenchmarkFamilies", {}]]],
  ["model_pool_v1.0.xlsx", "Frozen Model Pool v1.0", [["Models", "ModelPool", {}]]],
  ["human_verification_log_v1.0.xlsx", "Frozen Human Verification Log v1.0", [["VerificationLog", "HumanVerificationLog", { statusColumns: ["human_verified", "verification_status"], bodyRowHeight: 42 }]]],
  ["modeling_readiness_gate_v1.0.xlsx", "Frozen Modeling Readiness Gate v1.0", [["Gate", "ModelingReadinessGate", { statusColumns: ["passed", "overall_status"] }], ["NetworkQC", "NetworkQC", {}]]],
];

for (const [file, title, specs] of frozenSpecs) {
  await createWorkbook(path.join(frozenDir, file), title, specs, ["Frozen status: FROZEN. Do not edit; create a new version for changes."]);
}

async function sha256(filePath) {
  const bytes = await fs.readFile(filePath);
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

const manifestDefinitions = [
  ["final_modeling_matrix_v1.0.xlsx", "Formal Q1 modeling matrix", "FinalModelingMatrix/StandardizedMatrix/Lineage", "Q1 formal modeling", 10, 25],
  ["raw_benchmark_data_v1.0.xlsx", "Frozen long-form raw evidence", "RawData CSV and Stage 4 verification writeback", "Traceability and audits", 242, 62],
  ["source_registry_v1.0.xlsx", "Frozen source registry", "Sources registry", "Source tracing and references", 19, 12],
  ["final_modeling_benchmark_manifest_v1.0.xlsx", "Exact-setting manifest", "ModelingBenchmarkManifest", "Benchmark definition lock", 21, 15],
  ["benchmark_family_manifest_v1.0.xlsx", "Benchmark family manifest", "BenchmarkFamilies", "Family-level weighting", 48, 16],
  ["model_pool_v1.0.xlsx", "Exact model version pool", "ModelPool", "Model identity lock", 10, 12],
  ["human_verification_log_v1.0.xlsx", "Team manual-verification writeback log", "164 selected record IDs", "Verification evidence", 164, 23],
  ["modeling_readiness_gate_v1.0.xlsx", "Formal readiness gate", "Stage 4 automated QC", "Proceed/hold decision", 10, 9],
  ["final_modeling_matrix_v1.0.csv", "Machine-readable frozen matrix", "FinalModelingMatrix", "Reproducible scripts", 10, 25],
  ["raw_benchmark_data_v1.0.csv", "Machine-readable raw evidence", "RawData", "Reproducible scripts", 242, 62],
  ["source_registry_v1.0.csv", "Machine-readable source registry", "Sources", "Reproducible scripts", 19, 12],
  ["final_modeling_benchmark_manifest_v1.0.csv", "Machine-readable setting manifest", "ModelingBenchmarkManifest", "Reproducible scripts", 21, 15],
  ["benchmark_family_manifest_v1.0.csv", "Machine-readable family manifest", "BenchmarkFamilies", "Reproducible scripts", 48, 16],
  ["analysis_bundle_v1.0.json", "Complete frozen structured analysis bundle", "Stage 4 finalization bundle", "Full reproducibility", 1, 3],
  ["README.md", "Freeze usage and governance notes", "Stage 4 requirements", "Package orientation", null, null],
];

const freezeRows = [];
for (const [filename, purpose, upstream, downstream, rowCount, columnCount] of manifestDefinitions) {
  const filePath = path.join(frozenDir, filename);
  freezeRows.push({
    filename,
    purpose,
    version: "v1.0",
    creation_date: metadata.data_freeze_date,
    row_count: rowCount,
    column_count: columnCount,
    file_hash: await sha256(filePath),
    upstream_source: upstream,
    downstream_usage: downstream,
    frozen_status: "FROZEN",
  });
}
freezeRows.push({
  filename: "data_freeze_manifest_v1.0.xlsx",
  purpose: "Freeze inventory and pre-manifest hashes",
  version: "v1.0",
  creation_date: metadata.data_freeze_date,
  row_count: manifestDefinitions.length + 1,
  column_count: 10,
  file_hash: "See SHA256SUMS_v1.0.txt (self-reference excluded)",
  upstream_source: "All frozen v1.0 artifacts",
  downstream_usage: "Integrity verification",
  frozen_status: "FROZEN",
});

const freezeColumns = ["filename", "purpose", "version", "creation_date", "row_count", "column_count", "file_hash", "upstream_source", "downstream_usage", "frozen_status"];
const freezeMatrix = [freezeColumns, ...freezeRows.map((row) => freezeColumns.map((key) => row[key]))];
const freezeWorkbook = Workbook.create();
writeReadme(freezeWorkbook, "Data Freeze Manifest v1.0", ["The workbook's own hash is recorded in SHA256SUMS_v1.0.txt to avoid self-reference."]);
const freezeSheet = freezeWorkbook.worksheets.add("FreezeManifest");
writeMatrix(freezeSheet, freezeMatrix, { statusColumns: ["frozen_status"] });
await saveWorkbook(freezeWorkbook, path.join(frozenDir, "data_freeze_manifest_v1.0.xlsx"));

async function removeInspectSidecars(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) await removeInspectSidecars(target);
    else if (entry.name.endsWith(".inspect.ndjson")) await fs.unlink(target);
  }
}

for (const directory of [
  path.join(root, "data", "raw"), path.join(root, "data", "processed"), path.join(root, "data", "final"),
  path.join(root, "paper_materials"), path.join(root, "submission_support"), frozenDir, mirrorDir,
]) await removeInspectSidecars(directory);

const frozenFiles = (await fs.readdir(frozenDir))
  .filter((name) => name !== "SHA256SUMS_v1.0.txt" && !name.endsWith(".inspect.ndjson"))
  .sort();
const hashLines = [];
for (const filename of frozenFiles) hashLines.push(`${await sha256(path.join(frozenDir, filename))}  ${filename}`);
await fs.writeFile(path.join(frozenDir, "SHA256SUMS_v1.0.txt"), `${hashLines.join("\n")}\n`, "utf8");

console.log(JSON.stringify({
  status: metadata.status,
  ordinaryWorkbooks: ordinarySpecs.length + 2,
  frozenWorkbooks: frozenSpecs.length + 1,
  totalWorkbook: totalPath,
  frozenHashEntries: hashLines.length,
}, null, 2));
