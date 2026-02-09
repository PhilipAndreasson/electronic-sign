"""Render character sequences into sign views using bitmap fonts."""

from __future__ import annotations

from fonts.glyphs import GLYPH_GAP, GLYPH_WIDTH, get_glyph, is_supported_char
from sign.pixel import COLS, ROWS, Pixel
from sign.view import View


def render_text(text: str) -> View:
    """Convert a string of supported characters into a View.

    Characters are rendered left-to-right using the bitmap font, separated
    by GLYPH_GAP pixel columns.  The rendered text is centred horizontally
    on the 36-column sign.

    Args:
        text: A string of characters that all have defined glyphs.

    Returns:
        A View with the rendered text.

    Raises:
        ValueError: If *text* is empty, contains unsupported characters,
            or the rendered width exceeds the sign's column count.
    """
    if not text:
        raise ValueError("Text must not be empty")

    unsupported = [ch for ch in text if not is_supported_char(ch)]
    if unsupported:
        raise ValueError(
            f"Unsupported characters: {unsupported}. "
            "Only A, B, C, 1, 2, 3 are available."
        )

    total_width = len(text) * GLYPH_WIDTH + (len(text) - 1) * GLYPH_GAP
    if total_width > COLS:
        raise ValueError(
            f"Rendered text is {total_width} columns wide, "
            f"but the sign only has {COLS} columns."
        )

    # Centre the rendered block on the sign.
    offset = (COLS - total_width) // 2

    pixels: list[Pixel] = []
    col_cursor = offset

    for ch in text:
        glyph = get_glyph(ch)
        for row_idx, row_str in enumerate(glyph):
            for col_idx, cell in enumerate(row_str):
                if cell != " ":
                    pixels.append(Pixel(row_idx, col_cursor + col_idx))
        col_cursor += GLYPH_WIDTH + GLYPH_GAP

    return View(pixels)
