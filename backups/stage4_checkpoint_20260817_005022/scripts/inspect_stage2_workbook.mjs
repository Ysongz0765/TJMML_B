import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.cwd();
const inputPath = path.join(root, "data", "final", "LLM_Benchmark_Evaluation_Dataset.xlsx");
const previewDir = path.join(root, ".stage3_work", "stage2_previews");
await fs.mkdir(previewDir, { recursive: true });

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const summary = await workbook.inspect({
  kind: "workbook,sheet,table,drawing",
  maxChars: 12000,
  tableMaxRows: 4,
  tableMaxCols: 8,
  tableMaxCellChars: 80,
});
console.log(summary.ndjson);

const sheetInspect = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 12000,
});
const sheetNames = sheetInspect.ndjson
  .trim()
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line))
  .filter((item) => item.kind === "sheet")
  .map((item) => item.name);
for (const sheetName of sheetNames) {
  const safeName = sheetName.replace(/[\\/:*?"<>|]/g, "_");
  const preview = await workbook.render({
    sheetName,
    autoCrop: "all",
    scale: 0.8,
    format: "png",
  });
  await fs.writeFile(
    path.join(previewDir, `${safeName}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

console.log(JSON.stringify({ sheetNames, previewDir }));
