"""View representation for the electronic sign display."""

from __future__ import annotations

from typing import Iterable

from sign.pixel import COLS, ROWS, Pixel

# Display characters for on/off pixels.
PIXEL_ON = "*"
PIXEL_OFF = " "


class View:
    """A single frame of the electronic sign: a 6×36 grid of on/off pixels.

    Internally the grid is stored as a set of active (on) pixel coordinates
    for memory efficiency.

    Examples:
        >>> v = View.from_pixel_coordinates("A0A1B0B1")
        >>> print(v.render())
        **                                  
        **                                  
        ...
    """

    def __init__(self, pixels: Iterable[Pixel] | None = None) -> None:
        self._active_pixels: set[Pixel] = set(pixels) if pixels else set()

    @classmethod
    def from_pixel_coordinates(cls, sequence: str) -> View:
        """Parse a coordinate sequence string into a View.

        The sequence is a concatenation of pixel coordinates such as
        ``A0A1B5F35``.  Each coordinate starts with a letter (A-F)
        followed by a column number (0-35).

        Args:
            sequence: The raw coordinate string.

        Returns:
            A new View with the specified pixels turned on.

        Raises:
            ValueError: If a coordinate in the sequence is invalid.
        """
        pixels = _parse_coordinate_sequence(sequence)
        return cls(pixels)

    def set_pixel(self, pixel: Pixel) -> None:
        """Turn on a pixel."""
        self._active_pixels.add(pixel)

    def clear_pixel(self, pixel: Pixel) -> None:
        """Turn off a pixel."""
        self._active_pixels.discard(pixel)

    def is_on(self, row: int, col: int) -> bool:
        """Check whether the pixel at (row, col) is turned on."""
        return Pixel(row, col) in self._active_pixels

    @property
    def active_pixels(self) -> frozenset[Pixel]:
        """Return an immutable snapshot of all active pixels."""
        return frozenset(self._active_pixels)

    def render(self, on_char: str = PIXEL_ON, off_char: str = PIXEL_OFF) -> str:
        """Render the view as a multi-line string.

        Args:
            on_char: Character used for active pixels (default ``*``).
            off_char: Character used for inactive pixels (default `` ``).

        Returns:
            A string with *ROWS* lines, each *COLS* characters wide.
        """
        lines: list[str] = []
        for row in range(ROWS):
            chars: list[str] = []
            for col in range(COLS):
                if Pixel(row, col) in self._active_pixels:
                    chars.append(on_char)
                else:
                    chars.append(off_char)
            lines.append("".join(chars))
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, View):
            return NotImplemented
        return self._active_pixels == other._active_pixels

    def __repr__(self) -> str:
        count = len(self._active_pixels)
        return f"View(active_pixels={count})"


def _parse_coordinate_sequence(sequence: str) -> list[Pixel]:
    """Tokenize and parse a raw coordinate sequence.

    A coordinate starts with a letter A-F and is followed by one or two
    digits.  Tokens are extracted greedily: each letter begins a new
    coordinate and consumes all following digit characters.
    """
    tokens = _tokenize(sequence)
    return [Pixel.from_string(t) for t in tokens]


def _tokenize(sequence: str) -> list[str]:
    """Split a raw coordinate string into individual coordinate tokens.

    Each token starts with a letter and includes all subsequent digits.
    """
    tokens: list[str] = []
    current: list[str] = []

    for ch in sequence:
        if ch.isalpha():
            # Start of a new token – flush previous.
            if current:
                tokens.append("".join(current))
            current = [ch]
        elif ch.isdigit():
            if not current:
                raise ValueError(
                    f"Unexpected digit '{ch}' without a preceding row letter"
                )
            current.append(ch)
        elif ch.isspace():
            # Allow (and ignore) whitespace between coordinates.
            continue
        else:
            raise ValueError(f"Unexpected character in sequence: '{ch}'")

    if current:
        tokens.append("".join(current))

    return tokens
