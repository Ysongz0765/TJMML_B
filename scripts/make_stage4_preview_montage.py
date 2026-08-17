from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".stage4_work" / "workbook_previews" / "data_final_LLM_Benchmark_Evaluation_Dataset.xlsx"
OUT = ROOT / ".stage4_work" / "stage4_integrated_workbook_montage.png"

files = sorted(SRC.glob("*.png"))
thumb_w, thumb_h = 400, 235
label_h, columns = 34, 4
rows = (len(files) + columns - 1) // columns
canvas = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), "white")
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
for index, file in enumerate(files):
    image = Image.open(file).convert("RGB")
    image.thumbnail((thumb_w - 12, thumb_h - 12))
    x = (index % columns) * thumb_w
    y = (index // columns) * (thumb_h + label_h)
    canvas.paste(image, (x + (thumb_w - image.width) // 2, y + 6))
    draw.rectangle((x, y, x + thumb_w - 1, y + thumb_h + label_h - 1), outline="#B8C2CC")
    draw.text((x + 8, y + thumb_h + 8), file.stem, fill="#1F2933", font=font)
canvas.save(OUT)
print(OUT)
