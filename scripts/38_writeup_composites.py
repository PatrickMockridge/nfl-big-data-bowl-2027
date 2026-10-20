"""Compose the three two-panel figures used by the Kaggle writeup.

The source figures already exist; this script only stacks them vertically and
adds panel labels. It does not regenerate any data.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "writeup" / "figures"

WIDTH = 1800
MARGIN = 60
HEADER = 72
GUTTER = 28
DIVIDER = "#c3c2b7"

PAIRS = {
    "measurement_panel": ("pressure_signal.png", "combine_linkage.png"),
    "pricing_allocation_panel": ("net_rent.png", "next_role_forest.png"),
    "gap_agent_panel": ("allocation_gap.png", "agentic_allocation.png"),
}


def _load(name: str) -> Image.Image:
    image = Image.open(FIG / name).convert("RGB")
    height = round(image.height * WIDTH / image.width)
    return image.resize((WIDTH, height), Image.LANCZOS)


def _font(size: int = 44) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def compose(name: str, a: str, b: str) -> None:
    top = _load(a)
    bottom = _load(b)
    label = _font()
    canvas_w = WIDTH + 2 * MARGIN
    canvas_h = MARGIN + HEADER + top.height + GUTTER + HEADER + bottom.height + MARGIN
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    y = MARGIN
    draw.text((MARGIN, y + 8), "A", fill="#0b0b0b", font=label)
    y += HEADER
    canvas.paste(top, (MARGIN, y))
    y += top.height + GUTTER // 2
    draw.line([(MARGIN, y), (MARGIN + WIDTH, y)], fill=DIVIDER, width=2)
    y += GUTTER // 2
    draw.text((MARGIN, y + 8), "B", fill="#0b0b0b", font=label)
    y += HEADER
    canvas.paste(bottom, (MARGIN, y))

    out = FIG / f"{name}.png"
    canvas.save(out, dpi=(220, 220))
    print(f"wrote {out.relative_to(ROOT)} ({canvas.width}x{canvas.height})")


def main() -> None:
    for name, (a, b) in PAIRS.items():
        compose(name, a, b)


if __name__ == "__main__":
    main()
