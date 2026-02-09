"""Bitmap font system for rendering text on the electronic sign.

This module provides glyph definitions and text-to-View rendering.
Each character is defined as a 5×6 bitmap pattern that gets translated
into Pixel coordinates.

Design decisions:
- Monospaced glyphs (all 5 columns wide) for consistent spacing
- 1-pixel gap between characters for readability
- Horizontal centering for aesthetic presentation
- Easy extensibility - just add to GLYPHS dict to support new characters
"""

from __future__ import annotations

from sign import COLS, Pixel, View

# Glyph dimensions (all characters use same dimensions for consistency)
GLYPH_WIDTH = 5
GLYPH_GAP = 1

# Bitmap font definition
# Each glyph is 6 rows × 5 columns, where '*' = pixel on, ' ' = pixel off
# To add new characters, simply add entries to this dictionary
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
    """Convert a text string into a View by rendering each character as a bitmap glyph.

    The text is rendered left-to-right with GLYPH_GAP pixels between characters,
    and horizontally centered on the sign for aesthetic presentation.

    Process:
    1. Validate all characters are supported
    2. Calculate total width (chars × width + gaps)
    3. Verify text fits within sign width
    4. Calculate horizontal centering offset
    5. Render each character's glyph pattern into Pixel coordinates

    Args:
        text: String of characters to render (case-insensitive)

    Returns:
        View with pixels set according to glyph patterns

    Raises:
        ValueError: If text is empty, contains unsupported characters,
                   or rendered width exceeds sign width
    """
    if not text:
        raise ValueError("Text cannot be empty")

    text_upper = text.upper()

    # Validate all characters are supported before attempting render
    unsupported_chars = [ch for ch in text_upper if ch not in GLYPHS]
    if unsupported_chars:
        supported = sorted(GLYPHS.keys())
        raise ValueError(f"Unsupported characters {unsupported_chars}. Available: {supported}")

    # Calculate total width: each char is GLYPH_WIDTH, with gaps between
    # Example: "ABC" = 5 + 1 + 5 + 1 + 5 = 17 columns
    total_width = len(text) * GLYPH_WIDTH + (len(text) - 1) * GLYPH_GAP

    # Ensure rendered text fits on sign
    if total_width > COLS:
        raise ValueError(f"Text width {total_width} exceeds sign width {COLS}")

    # Center text horizontally on the sign for better aesthetics
    # Example: 36-col sign with 17-col text → offset = (36-17)//2 = 9
    horizontal_offset = (COLS - total_width) // 2

    pixels: list[Pixel] = []
    current_col = horizontal_offset

    # Render each character in sequence
    for char in text_upper:
        glyph_rows = GLYPHS[char]

        # Process each row of the glyph (6 rows per character)
        for row_index, row_pattern in enumerate(glyph_rows):
            # Check each cell in the row (5 cells per row)
            for col_offset, cell in enumerate(row_pattern):
                # '*' indicates pixel should be on
                if cell != " ":
                    pixels.append(Pixel(row_index, current_col + col_offset))

        # Move cursor right for next character (width + gap)
        current_col += GLYPH_WIDTH + GLYPH_GAP

    return View(pixels)
