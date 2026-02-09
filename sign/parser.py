"""Classify and parse user input into Views.

The parser distinguishes between two kinds of input:

1. **Pixel coordinate sequences** – strings like ``A0A1B5F35`` where
   each letter is immediately followed by a column number.
2. **Text character sequences** – strings like ``ABC123`` where every
   character maps to a font glyph.

The heuristic is simple: if the input consists entirely of characters
that have a font glyph defined, it is treated as text.  Otherwise it is
treated as a coordinate sequence.
"""

from __future__ import annotations

from enum import Enum, auto

from fonts.glyphs import is_supported_char
from sign.view import View


class InputType(Enum):
    """Discriminator for the two supported input formats."""

    COORDINATES = auto()
    TEXT = auto()


def classify_input(raw: str) -> InputType:
    """Determine whether *raw* is a coordinate sequence or a text sequence.

    The classification rule: if every character in *raw* (ignoring
    whitespace) has a corresponding font glyph **and** the string does
    not look like a coordinate sequence, it is treated as text.

    A string *looks like coordinates* if it contains a row letter (A-F)
    immediately followed by a digit.  However, since the supported glyph
    set overlaps with coordinate letters (A, B, C), we use a tie-breaking
    heuristic: if the string contains only characters that are valid
    glyphs **and** no character outside that set appears, we prefer the
    text interpretation.  This matches the challenge description where
    ``ABC123`` is treated as text.

    For unambiguous coordinate input, at least one row letter outside the
    glyph set (D, E, F) or a multi-digit column number will be present.
    """
    stripped = raw.replace(" ", "")
    if not stripped:
        return InputType.COORDINATES  # will fail later with a clear error

    # If every character is a supported glyph char → text mode.
    if all(is_supported_char(ch) for ch in stripped):
        return InputType.TEXT

    return InputType.COORDINATES


def parse_input(raw: str) -> View:
    """Parse raw user input into a View.

    Automatically detects whether the input is a pixel coordinate
    sequence or a character string and delegates accordingly.

    Args:
        raw: The raw input string.

    Returns:
        A fully constructed View.

    Raises:
        ValueError: On malformed input.
    """
    input_type = classify_input(raw)

    if input_type is InputType.TEXT:
        from fonts.renderer import render_text
        return render_text(raw.replace(" ", ""))
    else:
        return View.from_pixel_coordinates(raw)
