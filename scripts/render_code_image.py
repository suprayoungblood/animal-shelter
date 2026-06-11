"""Render a polished, editor-style PNG of selected source files.

Used to generate screenshots/code_view.png for the README. Not part of the app.

Run with:
    python3 scripts/render_code_image.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "screenshots" / "code_view.png"

BG = (15, 23, 42)            # slate-900
PANEL = (30, 41, 59)         # slate-800
GUTTER = (51, 65, 85)        # slate-700
TEXT = (241, 245, 249)       # slate-100
MUTED = (148, 163, 184)      # slate-400
ACCENT = (56, 189, 248)      # sky-400
KEYWORD = (244, 114, 182)    # pink-400
STRING = (134, 239, 172)     # green-300
COMMENT = (100, 116, 139)    # slate-500
NUMBER = (251, 191, 36)      # amber-400

KEYWORDS = {
    "def", "class", "import", "from", "return", "if", "elif", "else",
    "for", "while", "try", "except", "raise", "pass", "as", "in", "is",
    "not", "and", "or", "with", "lambda", "True", "False", "None", "self",
}

FILES = [
    ROOT / "animals" / "dog.py",
    ROOT / "kennel" / "kennel.py",
    ROOT / "gui" / "app.py",
]

FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/Library/Fonts/Courier New.ttf",
]

FONT_SIZE = 14
LINE_HEIGHT = 20
PADDING_X = 24
PADDING_Y = 18
GUTTER_WIDTH = 56
TAB_HEIGHT = 36
MAX_LINES_PER_FILE = 32
COLUMN_WIDTH = 560


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the first available monospaced system font."""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tokenize(line: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Naively tokenize a line into colored chunks. No regex — char scan."""
    tokens: list[tuple[str, tuple[int, int, int]]] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "#":
            tokens.append((line[i:], COMMENT))
            return tokens
        if ch in ('"', "'"):
            end = _find_string_end(line, i + 1, ch)
            tokens.append((line[i:end], STRING))
            i = end
            continue
        if ch.isalpha() or ch == "_":
            end = _scan_ident(line, i)
            word = line[i:end]
            color = KEYWORD if word in KEYWORDS else TEXT
            tokens.append((word, color))
            i = end
            continue
        if ch.isdigit():
            end = _scan_number(line, i)
            tokens.append((line[i:end], NUMBER))
            i = end
            continue
        tokens.append((ch, MUTED))
        i += 1
    return tokens


def _find_string_end(line: str, start: int, quote: str) -> int:
    """Return index just past the closing quote (or end of line)."""
    i = start
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == quote:
            return i + 1
        i += 1
    return len(line)


def _scan_ident(line: str, start: int) -> int:
    """Return index just past the identifier starting at start."""
    i = start
    while i < len(line) and (line[i].isalnum() or line[i] == "_"):
        i += 1
    return i


def _scan_number(line: str, start: int) -> int:
    """Return index just past the numeric literal starting at start."""
    i = start
    while i < len(line) and (line[i].isdigit() or line[i] == "."):
        i += 1
    return i


def render_file(path: Path, font: ImageFont.FreeTypeFont) -> Image.Image:
    """Render a single source file into an editor-style panel image."""
    raw_lines = path.read_text().splitlines()[:MAX_LINES_PER_FILE]
    height = TAB_HEIGHT + PADDING_Y * 2 + LINE_HEIGHT * len(raw_lines)
    img = Image.new("RGB", (COLUMN_WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    _draw_tab(draw, path, font)
    draw.rectangle(
        [(0, TAB_HEIGHT), (GUTTER_WIDTH, height)], fill=GUTTER
    )
    for i, line in enumerate(raw_lines):
        y = TAB_HEIGHT + PADDING_Y + i * LINE_HEIGHT
        _draw_line_number(draw, i + 1, y, font)
        _draw_line(draw, line, y, font)
    return img


def _draw_tab(draw: ImageDraw.ImageDraw, path: Path, font: ImageFont.FreeTypeFont) -> None:
    """Draw the file-name tab at the top of the panel."""
    draw.rectangle([(0, 0), (COLUMN_WIDTH, TAB_HEIGHT)], fill=PANEL)
    label = f"{path.parent.name}/{path.name}"
    draw.text((PADDING_X, 10), label, fill=ACCENT, font=font)


def _draw_line_number(
    draw: ImageDraw.ImageDraw, n: int, y: int, font: ImageFont.FreeTypeFont
) -> None:
    """Draw a right-aligned gutter line number."""
    text = str(n).rjust(3)
    draw.text((8, y), text, fill=MUTED, font=font)


def _draw_line(
    draw: ImageDraw.ImageDraw, line: str, y: int, font: ImageFont.FreeTypeFont
) -> None:
    """Draw one tokenized source line."""
    x = GUTTER_WIDTH + 12
    for chunk, color in tokenize(line):
        draw.text((x, y), chunk, fill=color, font=font)
        x += int(draw.textlength(chunk, font=font))


def compose(panels: list[Image.Image]) -> Image.Image:
    """Stack panels vertically with a margin."""
    gap = 16
    total_height = sum(p.height for p in panels) + gap * (len(panels) + 1)
    canvas = Image.new("RGB", (COLUMN_WIDTH + gap * 2, total_height), BG)
    y = gap
    for panel in panels:
        canvas.paste(panel, (gap, y))
        y += panel.height + gap
    return canvas


def main() -> None:
    font = load_font(FONT_SIZE)
    panels = [render_file(p, font) for p in FILES]
    image = compose(panels)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({image.size[0]}x{image.size[1]})")


if __name__ == "__main__":
    sys.exit(main())
