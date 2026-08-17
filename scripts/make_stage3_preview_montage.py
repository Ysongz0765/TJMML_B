from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / ".stage3_work" / "stage2_previews"
    files = sorted(source.glob("*.png"))
    if not files:
        raise SystemExit("No stage2 preview images found")

    thumb_w, thumb_h = 480, 280
    label_h = 34
    cols = 4
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for idx, file in enumerate(files):
        image = Image.open(file).convert("RGB")
        image.thumbnail((thumb_w - 16, thumb_h - 16))
        col, row = idx % cols, idx // cols
        x = col * thumb_w + (thumb_w - image.width) // 2
        y = row * (thumb_h + label_h) + (thumb_h - image.height) // 2
        canvas.paste(image, (x, y))
        draw.text((col * thumb_w + 8, row * (thumb_h + label_h) + thumb_h + 8), file.stem, fill="black", font=font)

    output = root / ".stage3_work" / "stage2_workbook_montage.png"
    canvas.save(output, dpi=(144, 144))
    print(output)


if __name__ == "__main__":
    main()
