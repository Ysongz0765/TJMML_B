import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.cwd();
const previewDir = path.join(root, ".stage4_work", "workbook_previews");
await fs.rm(previewDir, { recursive: true, force: true });
await fs.mkdir(previewDir, { recursive: true });

const workbookPaths = [
  "data/final/LLM_Benchmark_Evaluation_Dataset.xlsx",
  "data/final/final_modeling_matrix.xlsx",
  "data/processed/human_verification_final_checklist.xlsx",
  "data/processed/modeling_readiness_gate.xlsx",
  "data/processed/final_traceability_report.xlsx",
  "frozen/v1.0/final_modeling_matrix_v1.0.xlsx",
  "frozen/v1.0/raw_benchmark_data_v1.0.xlsx",
  "frozen/v1.0/source_registry_v1.0.xlsx",
  "frozen/v1.0/final_modeling_benchmark_manifest_v1.0.xlsx",
  "frozen/v1.0/benchmark_family_manifest_v1.0.xlsx",
  "frozen/v1.0/model_pool_v1.0.xlsx",
  "frozen/v1.0/human_verification_log_v1.0.xlsx",
  "frozen/v1.0/modeling_readiness_gate_v1.0.xlsx",
  "frozen/v1.0/data_freeze_manifest_v1.0.xlsx",
  "paper_materials/paper_table_data_sources.xlsx",
  "paper_materials/appendix_A_benchmark_system.xlsx",
  "paper_materials/appendix_B_source_mapping.xlsx",
  "paper_materials/source_reference_mapping.xlsx",
  "paper_materials/appendix_C_model_versions.xlsx",
  "paper_materials/data_section/data_source_table.xlsx",
  "paper_materials/data_section/benchmark_system_table.xlsx",
  "paper_materials/data_section/model_versions_table.xlsx",
  "paper_materials/data_section/source_mapping_table.xlsx",
  "submission_support/02_sources/source_location_registry.xlsx",
];

const results = [];
let totalSheetsRendered = 0;
let errorMatches = 0;

for (const relativePath of workbookPaths) {
  const inputPath = path.join(root, relativePath);
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
  const sheetInspection = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 30000 });
  const sheetNames = sheetInspection.ndjson.trim().split("\n").filter(Boolean).map((line) => JSON.parse(line))
    .filter((row) => row.kind === "sheet").map((row) => row.name);
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 1000 },
    summary: "Stage 4 final formula error scan",
    maxChars: 12000,
  });
  const errorLines = errors.ndjson.trim().split("\n").filter(Boolean)
    .map((line) => JSON.parse(line)).filter((row) => row.kind !== "notice");
  errorMatches += errorLines.length;

  const bookDir = path.join(previewDir, relativePath.replace(/[\\/:*?"<>|]/g, "_"));
  await fs.mkdir(bookDir, { recursive: true });
  for (const sheetName of sheetNames) {
    const safeName = sheetName.replace(/[\\/:*?"<>|]/g, "_");
    const image = await workbook.render({ sheetName, autoCrop: "all", scale: 0.65, format: "png" });
    await fs.writeFile(path.join(bookDir, `${safeName}.png`), new Uint8Array(await image.arrayBuffer()));
    totalSheetsRendered += 1;
  }

  const firstSheet = sheetNames[0];
  const keyRegion = await workbook.inspect({ kind: "region", sheetId: firstSheet, range: "A1:L18", maxChars: 7000 });
  results.push({ relativePath, sheetCount: sheetNames.length, sheetNames, errorScan: errors.ndjson, keyRegion: keyRegion.ndjson });
}

const totalWorkbook = results.find((item) => item.relativePath === "data/final/LLM_Benchmark_Evaluation_Dataset.xlsx");
const report = {
  status: errorMatches === 0 ? "PASS" : "REVIEW_REQUIRED",
  workbooksChecked: results.length,
  sheetsRendered: totalSheetsRendered,
  integratedWorkbookSheetCount: totalWorkbook?.sheetCount ?? 0,
  previewDir,
  formulaErrorMatches: errorMatches,
  workbooks: results,
};
await fs.writeFile(path.join(root, "reports", "stage4_workbook_qc.json"), JSON.stringify(report, null, 2), "utf8");
console.log(JSON.stringify({
  status: report.status,
  workbooksChecked: report.workbooksChecked,
  sheetsRendered: report.sheetsRendered,
  integratedWorkbookSheetCount: report.integratedWorkbookSheetCount,
  formulaErrorMatches: report.formulaErrorMatches,
  previewDir,
}, null, 2));
if (report.status !== "PASS") process.exitCode = 1;
