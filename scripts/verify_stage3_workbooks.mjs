import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.cwd();
const inputPath = path.join(root, "data", "final", "LLM_Benchmark_Evaluation_Dataset.xlsx");
const previewDir = path.join(root, ".stage3_work", "final_previews");
const relativePath = (value) => path.relative(root, value).split(path.sep).join("/");
await fs.rm(previewDir, { recursive: true, force: true });
await fs.mkdir(previewDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheets = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 20000 });
const sheetNames = sheets.ndjson.trim().split("\n").filter(Boolean).map((line) => JSON.parse(line))
  .filter((row) => row.kind === "sheet").map((row) => row.name);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 1000 },
  summary: "final formula error scan",
  maxChars: 12000,
});

for (const sheetName of sheetNames) {
  const safe = sheetName.replace(/[\\/:*?"<>|]/g, "_");
  const image = await workbook.render({ sheetName, autoCrop: "all", scale: 0.7, format: "png" });
  await fs.writeFile(path.join(previewDir, `${safe}.png`), new Uint8Array(await image.arrayBuffer()));
}

const keyRegions = {};
for (const [sheetId, range] of [
  ["README", "A1:B18"],
  ["FinalModelingMatrix", "A1:Y11"],
  ["ModelingBenchmarkManifest", "A1:Q24"],
  ["ModelingReadinessGate", "A1:G12"],
  ["RawData", "A1:BD8"],
]) {
  const inspected = await workbook.inspect({ kind: "region", sheetId, range, maxChars: 9000 });
  keyRegions[sheetId] = inspected.ndjson;
}

const result = {
  inputPath: relativePath(inputPath),
  sheetCount: sheetNames.length,
  sheetNames,
  previewDir: relativePath(previewDir),
  errorScan: errors.ndjson,
  keyRegions,
};
await fs.writeFile(path.join(root, "reports", "stage3_workbook_qc.json"), JSON.stringify(result, null, 2), "utf8");
console.log(JSON.stringify({
  sheetCount: sheetNames.length,
  sheetNames,
  previewDir: relativePath(previewDir),
  errorScan: errors.ndjson,
}));
