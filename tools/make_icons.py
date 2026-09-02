"""Generate the home-screen icons for the installable app.

    python tools/make_icons.py

Writes PNGs into web/public/. Committed as a script rather than as binaries
alone so the design can be changed and regenerated rather than reverse
engineered out of a base64 blob.

The mark is a white partial-derivative sign on the app's indigo, over the same
faint ruled grid the interface uses. Chosen because it reads at 60px on a home
screen where "d/dx" would not, it is unmistakably calculus rather than generic
mathematics, and it is the symbol Acts IV and V are built on.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "public"

INDIGO = (47, 73, 201)
WHITE = (255, 255, 255)
GRID = (255, 255, 255, 26)  # ~10% white

# A serif face, to match the app's Spectral display type. Windows first, then
# the usual Linux and macOS locations, so this runs anywhere.
FONT_CANDIDATES = (
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/times.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
)


def find_font() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    raise SystemExit(
        "no serif font found. Add one to FONT_CANDIDATES in tools/make_icons.py."
    )


def draw_icon(size: int, *, maskable: bool, font_path: str) -> Image.Image:
    image = Image.new("RGB", (size, size), INDIGO)
    draw = ImageDraw.Draw(image, "RGBA")

    # The ruled grid, echoing the squared-paper identity of the interface.
    step = size / 8
    line = max(1, size // 128)
    for i in range(1, 8):
        offset = round(i * step)
        draw.line([(offset, 0), (offset, size)], fill=GRID, width=line)
        draw.line([(0, offset), (size, offset)], fill=GRID, width=line)

    # Android crops maskable icons to a circle, so the glyph shrinks into the
    # safe zone rather than losing its edges.
    glyph_size = round(size * (0.44 if maskable else 0.62))
    font = ImageFont.truetype(font_path, glyph_size)

    # Centre on the glyph's actual ink, not on its font metrics: the partial
    # sign sits high in its em box, and centring by metrics leaves it visibly
    # low in the tile.
    left, top, right, bottom = draw.textbbox((0, 0), "\u2202", font=font)
    x = (size - (right - left)) / 2 - left
    y = (size - (bottom - top)) / 2 - top
    draw.text((x, y), "\u2202", font=font, fill=WHITE)

    return image


def main() -> int:
    font_path = find_font()
    OUT.mkdir(parents=True, exist_ok=True)

    # 192 and 512 for the web manifest; 180 is what iOS wants for
    # apple-touch-icon, and iOS ignores the manifest for the home-screen icon.
    targets = (
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, True),
        ("apple-touch-icon.png", 180, False),
    )

    for name, size, maskable in targets:
        path = OUT / name
        draw_icon(size, maskable=maskable, font_path=font_path).save(
            path, "PNG", optimize=True
        )
        print(f"  {name:<22} {size}x{size}  {path.stat().st_size // 1024 or 1} KB")

    print(f"icons written to {OUT.relative_to(ROOT)} using {Path(font_path).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
