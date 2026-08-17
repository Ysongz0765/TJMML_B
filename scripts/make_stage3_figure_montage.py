from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "figures" / "stage3"
OUTPUT = ROOT / ".stage3_work" / "stage3_paper_figures_montage.png"
files = sorted(SOURCE.glob("*.png"))
width, height, label_height, columns = 480, 300, 30, 3
rows = (len(files) + columns - 1) // columns
canvas = Image.new("RGB", (columns * width, rows * (height + label_height)), "white")
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()
for index, file in enumerate(files):
    image = Image.open(file).convert("RGB")
    image.thumbnail((width - 12, height - 12))
    x = (index % columns) * width
    y = (index // columns) * (height + label_height)
    canvas.paste(image, (x + (width - image.width) // 2, y + (height - image.height) // 2))
    draw.rectangle((x, y, x + width - 1, y + height + label_height - 1), outline="#B8C2CC")
    draw.text((x + 8, y + height + 7), file.stem, fill="#1F2933", font=font)
canvas.save(OUTPUT)
print(OUTPUT)
