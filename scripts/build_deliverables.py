"""Render code and output screenshots into the Desktop deliverable folders.

Produces, on the Desktop under Animal_Shelter_Simulator/:
  Code/         editor-style PNGs of each source file
  Application/  terminal-style PNGs of the real program + test output

Run with:
    python3 scripts/build_deliverables.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = Path.home() / "Desktop" / "Animal_Shelter_Simulator"
CODE_DIR = DESKTOP / "Code"
APP_DIR = DESKTOP / "Application"

# ---- palette -------------------------------------------------------------
BG = (15, 23, 42)
PANEL = (30, 41, 59)
GUTTER = (51, 65, 85)
TEXT = (241, 245, 249)
MUTED = (148, 163, 184)
ACCENT = (56, 189, 248)
KEYWORD = (244, 114, 182)
STRING = (134, 239, 172)
COMMENT = (100, 116, 139)
NUMBER = (251, 191, 36)
TERM_BG = (12, 17, 28)
PROMPT = (94, 234, 212)
DOT_RED = (255, 95, 86)
DOT_YELLOW = (255, 189, 46)
DOT_GREEN = (39, 201, 63)

KEYWORDS = {
    "def", "class", "import", "from", "return", "if", "elif", "else",
    "for", "while", "try", "except", "raise", "pass", "as", "in", "is",
    "not", "and", "or", "with", "lambda", "True", "False", "None", "self",
    "assert",
}

FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/Library/Fonts/Courier New.ttf",
]

FONT_SIZE = 15
LINE_HEIGHT = 22
GUTTER_WIDTH = 56
TAB_HEIGHT = 40
PADDING_Y = 18
CHAR_PAD = 18

CODE_FILES = [
    ROOT / "animals" / "dog.py",
    ROOT / "animals" / "cat.py",
    ROOT / "animals" / "bird.py",
    ROOT / "kennel" / "kennel.py",
    ROOT / "demo.py",
    ROOT / "tests" / "test_animals.py",
    ROOT / "tests" / "test_kennel.py",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load the first available monospaced system font."""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ---- syntax tokenizer (char scan, no regex) ------------------------------
def tokenize(line: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Naively tokenize a line into colored chunks."""
    tokens: list[tuple[str, tuple[int, int, int]]] = []
    i, n = 0, len(line)
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
            tokens.append((word, KEYWORD if word in KEYWORDS else TEXT))
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
    i = start
    while i < len(line) and (line[i].isalnum() or line[i] == "_"):
        i += 1
    return i


def _scan_number(line: str, start: int) -> int:
    i = start
    while i < len(line) and (line[i].isdigit() or line[i] == "."):
        i += 1
    return i


def _char_width(font: ImageFont.FreeTypeFont) -> int:
    """Width of a single monospaced character."""
    return int(font.getlength("M"))


def render_code(path: Path, font: ImageFont.FreeTypeFont, out_path: Path) -> None:
    """Render a full source file into an editor-style PNG."""
    lines = path.read_text().splitlines() or [""]
    char_w = _char_width(font)
    longest = max(len(line) for line in lines)
    width = GUTTER_WIDTH + CHAR_PAD + char_w * max(longest, 40) + CHAR_PAD
    height = TAB_HEIGHT + PADDING_Y * 2 + LINE_HEIGHT * len(lines)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # filename tab
    draw.rectangle([(0, 0), (width, TAB_HEIGHT)], fill=PANEL)
    label = f"{path.parent.name}/{path.name}"
    draw.text((CHAR_PAD, 12), label, fill=ACCENT, font=font)

    # gutter
    draw.rectangle([(0, TAB_HEIGHT), (GUTTER_WIDTH, height)], fill=GUTTER)

    for i, line in enumerate(lines):
        y = TAB_HEIGHT + PADDING_Y + i * LINE_HEIGHT
        draw.text((8, y), str(i + 1).rjust(3), fill=MUTED, font=font)
        x = GUTTER_WIDTH + CHAR_PAD
        for chunk, color in tokenize(line):
            draw.text((x, y), chunk, fill=color, font=font)
            x += int(draw.textlength(chunk, font=font))

    img.save(out_path)
    print(f"  code  -> {out_path.relative_to(DESKTOP.parent)}  ({width}x{height})")


def render_terminal(
    command: str, output: str, font: ImageFont.FreeTypeFont, out_path: Path
) -> None:
    """Render a real command and its captured output as a terminal PNG."""
    body_lines = [f"$ {command}", ""] + output.rstrip("\n").splitlines()
    char_w = _char_width(font)
    longest = max((len(line) for line in body_lines), default=40)
    width = CHAR_PAD * 2 + char_w * max(longest, 50)
    height = TAB_HEIGHT + PADDING_Y * 2 + LINE_HEIGHT * len(body_lines)
    img = Image.new("RGB", (width, height), TERM_BG)
    draw = ImageDraw.Draw(img)

    # title bar with traffic-light dots
    draw.rectangle([(0, 0), (width, TAB_HEIGHT)], fill=PANEL)
    for idx, color in enumerate((DOT_RED, DOT_YELLOW, DOT_GREEN)):
        cx = 20 + idx * 22
        draw.ellipse([(cx, 14), (cx + 12, 26)], fill=color)
    draw.text((90, 12), "Terminal — Animal Shelter Simulator", fill=MUTED, font=font)

    for i, line in enumerate(body_lines):
        y = TAB_HEIGHT + PADDING_Y + i * LINE_HEIGHT
        color = PROMPT if line.startswith("$") else TEXT
        if "ok" in line or line.strip() == "OK" or "Rejected as expected" in line:
            color = STRING
        draw.text((CHAR_PAD, y), line, fill=color, font=font)

    img.save(out_path)
    print(f"  out   -> {out_path.relative_to(DESKTOP.parent)}  ({width}x{height})")


def run(command: list[str]) -> str:
    """Run a command from the project root and return combined output."""
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True
    )
    return (result.stdout + result.stderr).rstrip("\n")


def main() -> None:
    CODE_DIR.mkdir(parents=True, exist_ok=True)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    font = load_font(FONT_SIZE)

    print("Rendering code screenshots:")
    for i, path in enumerate(CODE_FILES, start=1):
        out = CODE_DIR / f"{i:02d}_{path.stem}.png"
        render_code(path, font, out)

    print("Rendering application/output screenshots:")
    demo_out = run([sys.executable, "demo.py"])
    render_terminal("python3 demo.py", demo_out, font, APP_DIR / "01_demo_output.png")

    test_out = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    render_terminal(
        "python3 -m unittest discover -s tests -v",
        test_out,
        font,
        APP_DIR / "02_unit_tests.png",
    )

    print(f"\nDone. Deliverables in: {DESKTOP}")


if __name__ == "__main__":
    main()
