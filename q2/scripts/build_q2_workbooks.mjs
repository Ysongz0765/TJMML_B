import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const dataDir = `${root}/q2/data`;
const previewDir = `${root}/q2/data/.previews`;

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const next = text[i + 1];
    if (quoted) {
      if (ch === '"' && next === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        cell += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(cell);
      cell = "";
    } else if (ch === "\n") {
      row.push(cell.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += ch;
    }
  }
  if (cell.length || row.length) {
    row.push(cell.replace(/\r$/, ""));
    rows.push(row);
  }
  if (rows.length && rows[0][0].charCodeAt(0) === 0xfeff) {
    rows[0][0] = rows[0][0].slice(1);
  }
  return rows;
}

function typed(value) {
  if (value === "") return null;
  if (value === "True" || value === "TRUE" || value === "true") return true;
  if (value === "False" || value === "FALSE" || value === "false") return false;
  const numeric = Number(value);
  if (value.trim() !== "" && Number.isFinite(numeric)) return numeric;
  return value;
}

async function csvToRows(path) {
  const text = await fs.readFile(path, "utf8");
  return parseCsv(text).map((row) => row.map(typed));
}

function styleSheet(sheet, rowCount, colCount) {
  const used = sheet.getRangeByIndexes(0, 0, rowCount, colCount);
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  sheet.getRangeByIndexes(0, 0, 1, colCount).format = {
    fill: "#1F4E78",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
    horizontalAlignment: "center",
  };
  used.format.borders = { preset: "insideHorizontal", style: "thin", color: "#E5E7EB" };
  used.format.font = { typeface: "Aptos", fontSize: 10 };
  used.format.autofitColumns();
  used.format.autofitRows();
  if (colCount > 2) {
    sheet.getRangeByIndexes(1, 2, Math.max(rowCount - 1, 1), colCount - 2).format.numberFormat = "0.000000";
  }
}

async function buildOne(csvName, xlsxName, sheetName) {
  const rows = await csvToRows(`${dataDir}/${csvName}`);
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add(sheetName);
  sheet.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;
  styleSheet(sheet, rows.length, rows[0].length);
  const inspect = await workbook.inspect({
    kind: "workbook,sheet,table,region,match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 50 },
    tableMaxRows: 12,
    tableMaxCols: Math.min(rows[0].length, 12),
    maxChars: 5000,
  });
  await fs.writeFile(`${dataDir}/${xlsxName}.inspect.ndjson`, inspect.ndjson, "utf8");
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${xlsxName}.png`, new Uint8Array(await preview.arrayBuffer()));
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(`${dataDir}/${xlsxName}`);
}

await fs.mkdir(previewDir, { recursive: true });
await buildOne("q1_capability_scores.csv", "q1_capability_scores.xlsx", "CapabilityScores");
await buildOne("q2_model_master_table.csv", "q2_model_master_table.xlsx", "Q2ModelMaster");
