"""Bitmap font definitions for letters and digits.

Each glyph is defined as a 6-row list of strings, where ``*`` represents
an active pixel and `` `` (space) an inactive one.  All glyphs are 5
columns wide.  A 1-column gap is inserted between glyphs when composing
a view.

The challenge requires at least A, B, C, 1, 2, 3.  Additional glyphs
can be added to this mapping to extend the sign's character support.
"""

# Character width (all glyphs are monospaced at this width).
GLYPH_WIDTH = 5

# Gap between rendered glyphs (in pixels/columns).
GLYPH_GAP = 1

# Each glyph: 6 rows, each row is a string of length GLYPH_WIDTH.
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


def is_supported_char(ch: str) -> bool:
    """Return True if a glyph is defined for the given character."""
    return ch.upper() in GLYPHS


def get_glyph(ch: str) -> list[str]:
    """Return the glyph rows for *ch*.

    Args:
        ch: A single character (case-insensitive).

    Returns:
        A list of 6 strings, each of length GLYPH_WIDTH.

    Raises:
        ValueError: If the character has no defined glyph.
    """
    key = ch.upper()
    if key not in GLYPHS:
        raise ValueError(
            f"No glyph defined for character '{ch}'. "
            f"Supported characters: {sorted(GLYPHS.keys())}"
        )
    return GLYPHS[key]
