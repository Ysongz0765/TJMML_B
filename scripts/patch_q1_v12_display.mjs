import fs from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const dir = path.join(root, "outputs", "q1_v1.2", ".build", "workbook_payloads");
const typeA = new Set(["deepseek_v4_pro_max", "deepseek_v4_flash_max", "glm_5_2_max"]);

function patchRecords(records) {
  return records.map((row) => {
    const next = { ...row };
    if (Object.prototype.hasOwnProperty.call(next, "C5")) {
      next["C5* 多模态有效能力"] = typeA.has(next.model_id) ? "0*" : next.C5;
      delete next.C5;
    }
    return next;
  });
}

for (const file of ["paper_table_q1_v12_ranking_A.xlsx.json", "paper_table_q1_v12_dimension_scores.xlsx.json"]) {
  const p = path.join(dir, file);
  const payload = JSON.parse(await fs.readFile(p, "utf8"));
  for (const sheet of payload.sheets) if (["Ranking_A", "Scores_A"].includes(sheet.name)) sheet.records = patchRecords(sheet.records);
  await fs.writeFile(p, JSON.stringify(payload, null, 2), "utf8");
}
