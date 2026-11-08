"""Generate the reproducible PNG examples used by the demos."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "examples" / "images"
BACKGROUND = "#f4f7fb"
INK = "#20324a"
BLUE = "#4d83d1"
GREEN = "#39a879"
ORANGE = "#e9a23b"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable font at the requested size."""
    return ImageFont.load_default(size=size)


def create_chart() -> None:
    """Render a labeled bar chart with unambiguous quarterly values."""
    image = Image.new("RGB", (1200, 800), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((76, 48), "Quarterly sales", font=_font(42), fill=INK)
    draw.text((78, 105), "Units sold by quarter", font=_font(24), fill="#64748b")

    left, top, chart_width, chart_height = 145, 190, 900, 475
    baseline = top + chart_height
    max_value = 50
    for value in range(0, max_value + 1, 10):
        y = baseline - int(chart_height * value / max_value)
        draw.line((left, y, left + chart_width, y), fill="#d7dfeb", width=2)
        draw.text((82, y - 11), str(value), font=_font(19), fill="#64748b")

    values = {"Q1": 24, "Q2": 31, "Q3": 18, "Q4": 42}
    slot_width = chart_width // len(values)
    bar_width = 112
    for index, (quarter, value) in enumerate(values.items()):
        center = left + slot_width * index + slot_width // 2
        bar_height = int(chart_height * value / max_value)
        bar_top = baseline - bar_height
        draw.rounded_rectangle(
            (center - bar_width // 2, bar_top, center + bar_width // 2, baseline),
            radius=12,
            fill=BLUE if quarter != "Q4" else GREEN,
        )
        draw.text(
            (center - 17, bar_top - 34),
            str(value),
            font=_font(22),
            fill=INK,
        )
        draw.text(
            (center - 25, baseline + 22),
            quarter,
            font=_font(22),
            fill=INK,
        )

    image.save(OUTPUT_DIR / "chart.png")


def create_spreadsheet() -> None:
    """Render a small, legible product-sales spreadsheet."""
    image = Image.new("RGB", (1200, 760), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((72, 48), "Store sales - sample sheet", font=_font(38), fill=INK)
    draw.text((74, 105), "Weekly units sold", font=_font(22), fill="#64748b")

    x_positions = (78, 500, 835, 1085)
    y = 185
    row_height = 86
    headers = ("Product", "Units sold", "Returns")
    draw.rounded_rectangle(
        (x_positions[0], y, x_positions[-1], y + row_height),
        radius=10,
        fill="#dce8f8",
    )
    for x, header in zip(x_positions[:-1], headers, strict=True):
        draw.text((x + 20, y + 28), header, font=_font(22), fill=INK)

    rows = (
        ("Notebook", "11", "1"),
        ("Water bottle", "8", "0"),
        ("Desk lamp", "3", "0"),
        ("Floor mat", "6", "1"),
    )
    for row_index, row in enumerate(rows):
        top = y + row_height * (row_index + 1)
        bottom = top + row_height
        draw.rectangle(
            (x_positions[0], top, x_positions[-1], bottom),
            fill="white",
            outline="#d7dfeb",
            width=2,
        )
        for column_index, (x, value) in enumerate(
            zip(x_positions[:-1], row, strict=True)
        ):
            is_top_seller = row_index == 0 and column_index == 1
            draw.text(
                (x + 20, top + 28),
                value,
                font=_font(22),
                fill=GREEN if is_top_seller else INK,
            )

    image.save(OUTPUT_DIR / "spreadsheet.png")


def create_dog() -> None:
    """Draw a simple cartoon dog on a contrasting background."""
    image = Image.new("RGB", (800, 800), "#e8f4e7")
    draw = ImageDraw.Draw(image)
    draw.ellipse((118, 570, 682, 725), fill="#cfe5c9")
    draw.ellipse((245, 380, 585, 655), fill="#bd7a43")
    draw.ellipse((300, 225, 595, 525), fill="#d79455")
    draw.ellipse((268, 220, 370, 390), fill="#8c5639")
    draw.ellipse((505, 220, 607, 390), fill="#8c5639")
    draw.ellipse((370, 380, 440, 448), fill="#f3d9b8")
    draw.ellipse((360, 337, 382, 360), fill=INK)
    draw.ellipse((506, 337, 528, 360), fill=INK)
    draw.ellipse((407, 402, 439, 426), fill="#392f2a")
    draw.arc((382, 415, 462, 475), start=5, end=165, fill="#392f2a", width=7)
    draw.line((320, 570, 309, 645), fill="#8c5639", width=34)
    draw.line((521, 570, 530, 645), fill="#8c5639", width=34)
    draw.arc((555, 420, 683, 575), start=185, end=345, fill="#8c5639", width=22)
    image.save(OUTPUT_DIR / "dog.png")


def create_bicycle() -> None:
    """Draw a side-on bicycle with two wheels and a clear frame."""
    image = Image.new("RGB", (800, 800), "#edf3fb")
    draw = ImageDraw.Draw(image)
    draw.ellipse((130, 430, 365, 665), outline="#34445b", width=18)
    draw.ellipse((465, 430, 700, 665), outline="#34445b", width=18)
    rear, crank, front, seat = (248, 548), (425, 548), (582, 548), (342, 370)
    frame_color = "#e4544f"
    draw.line((rear, seat, crank, rear), fill=frame_color, width=17, joint="curve")
    draw.line((seat, front, crank), fill=frame_color, width=17, joint="curve")
    draw.line((seat, (335, 342)), fill="#34445b", width=18)
    draw.line(((300, 342), (370, 342)), fill="#34445b", width=16)
    draw.line((front, (612, 370)), fill="#34445b", width=16)
    draw.line(((584, 370), (635, 370), (653, 398)), fill="#34445b", width=14)
    draw.ellipse((408, 531, 442, 565), fill=ORANGE)
    draw.line(((425, 548), (456, 578)), fill="#34445b", width=10)
    draw.line(((425, 548), (396, 518)), fill="#34445b", width=10)
    draw.line(((456, 578), (478, 578)), fill="#34445b", width=9)
    draw.line(((396, 518), (373, 518)), fill="#34445b", width=9)
    image.save(OUTPUT_DIR / "bicycle.png")


def create_mug() -> None:
    """Draw a single blue ceramic mug on a simple tabletop."""
    image = Image.new("RGB", (800, 800), "#f6f1e8")
    draw = ImageDraw.Draw(image)
    draw.ellipse((120, 600, 680, 705), fill="#e1d6c6")
    draw.ellipse((270, 245, 535, 318), fill="#3c74b9")
    draw.rectangle((270, 280, 535, 570), fill="#3c74b9")
    draw.ellipse((270, 530, 535, 610), fill="#315f99")
    draw.ellipse((470, 340, 640, 520), fill="#f6f1e8")
    draw.ellipse((490, 360, 620, 500), fill="#3c74b9")
    draw.ellipse((290, 252, 515, 304), fill="#1e3d60")
    draw.arc((312, 257, 490, 297), start=185, end=355, fill="#d7eaff", width=6)
    image.save(OUTPUT_DIR / "mug.png")


def main() -> None:
    """Write all five sample images to the repository examples directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_chart()
    create_spreadsheet()
    create_dog()
    create_bicycle()
    create_mug()
    print(f"Wrote sample images to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
