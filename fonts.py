from __future__ import annotations

from sign import COLS, Pixel, View

GLYPH_WIDTH = 5
GLYPH_GAP = 1

GLYPHS: dict[str, list[str]] = {
    "A": [
        " *** ",
        "*   *",
        "*****",
        "*   *",
        "*   *",
        "*   *",
    ],
    "B": [
        "**** ",
        "*   *",
        "**** ",
        "*   *",
        "*   *",
        "**** ",
    ],
    "C": [
        " *** ",
        "*   *",
        "*    ",
        "*    ",
        "*   *",
        " *** ",
    ],
    "1": [
        "  *  ",
        " **  ",
        "  *  ",
        "  *  ",
        "  *  ",
        " *** ",
    ],
    "2": [
        " *** ",
        "*   *",
        "   * ",
        "  *  ",
        " *   ",
        "*****",
    ],
    "3": [
        " *** ",
        "*   *",
        "  ** ",
        "    *",
        "*   *",
        " *** ",
    ],
}


def render_text(text: str) -> View:
    """Convert text to View using bitmap glyphs. Text is centered on sign."""
    if not text:
        raise ValueError("Text cannot be empty")

    text_upper = text.upper()
    unsupported_chars = [ch for ch in text_upper if ch not in GLYPHS]
    if unsupported_chars:
        supported = sorted(GLYPHS.keys())
        raise ValueError(f"Unsupported characters {unsupported_chars}. Available: {supported}")

    total_width = len(text) * GLYPH_WIDTH + (len(text) - 1) * GLYPH_GAP
    if total_width > COLS:
        raise ValueError(f"Text width {total_width} exceeds sign width {COLS}")

    horizontal_offset = (COLS - total_width) // 2
    pixels: list[Pixel] = []
    current_col = horizontal_offset

    for char in text_upper:
        glyph_rows = GLYPHS[char]
        for row_index, row_pattern in enumerate(glyph_rows):
            for col_offset, cell in enumerate(row_pattern):
                if cell != " ":
                    pixels.append(Pixel(row_index, current_col + col_offset))
        current_col += GLYPH_WIDTH + GLYPH_GAP

    return View(pixels)
