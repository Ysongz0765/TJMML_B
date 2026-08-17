import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const payloadDir = path.join(root, "outputs", "q1_v1.2", ".build", "workbook_payloads");
const outDir = path.join(root, "outputs", "q1_v1.2", "tables");
const previewDir = path.join(root, "outputs", "q1_v1.2", ".build", "workbook_previews");
await fs.mkdir(outDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

function columnName(n) {
  let s = "";
  for (let x = n + 1; x > 0; x = Math.floor((x - 1) / 26)) s = String.fromCharCode(65 + ((x - 1) % 26)) + s;
  return s;
}

function valueRows(records) {
  const keys = [];
  for (const record of records) for (const key of Object.keys(record)) if (!keys.includes(key)) keys.push(key);
  return { keys, rows: records.map((record) => keys.map((key) => record[key] ?? null)) };
}

const payloadFiles = (await fs.readdir(payloadDir)).filter((name) => name.endsWith(".json")).sort();
const created = [];
for (const payloadFile of payloadFiles) {
  const payload = JSON.parse(await fs.readFile(path.join(payloadDir, payloadFile), "utf8"));
  const workbook = Workbook.create();
  for (const sheetPayload of payload.sheets) {
    const sheet = workbook.worksheets.add(String(sheetPayload.name).slice(0, 31));
    sheet.showGridLines = false;
    const { keys, rows } = valueRows(sheetPayload.records ?? []);
    const matrix = [keys, ...rows];
    if (matrix.length && keys.length) {
      const end = `${columnName(keys.length - 1)}${matrix.length}`;
      const range = sheet.getRange(`A1:${end}`);
      range.values = matrix;
      range.format.wrapText = true;
      range.format.font = { name: "Aptos", size: 10, color: "#1F2937" };
      sheet.getRange(`A1:${columnName(keys.length - 1)}1`).format = {
        fill: "#1F4E78",
        font: { name: "Aptos Display", size: 10, bold: true, color: "#FFFFFF" },
        horizontalAlignment: "center",
        verticalAlignment: "center",
        wrapText: true,
        borders: { preset: "outside", style: "thin", color: "#17365D" },
      };
      range.format.borders = { preset: "insideHorizontal", style: "thin", color: "#D9E2F3" };
      range.format.autofitColumns();
      range.format.autofitRows();
      if (keys.length) sheet.getRange(`A:${columnName(keys.length - 1)}`).format.columnWidth = 18;
      sheet.getRange(`A1:${columnName(keys.length - 1)}1`).format.rowHeight = 30;
      sheet.freezePanes.freezeRows(1);
    }
  }
  const inspect = await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 5000, tableMaxRows: 3, tableMaxCols: 8 });
  const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
  await fs.writeFile(path.join(previewDir, `${payload.filename}.inspect.ndjson`), `${inspect.ndjson}\n${errors.ndjson}`);
  for (const sheetPayload of payload.sheets) {
    const preview = await workbook.render({ sheetName: String(sheetPayload.name).slice(0, 31), autoCrop: "all", scale: 1, format: "png" });
    const bytes = new Uint8Array(await preview.arrayBuffer());
    await fs.writeFile(path.join(previewDir, `${payload.filename}.${String(sheetPayload.name).slice(0, 20)}.png`), bytes);
  }
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(outDir, payload.filename));
  created.push(payload.filename);
}
console.log(JSON.stringify({ created, count: created.length, outDir }, null, 2));
