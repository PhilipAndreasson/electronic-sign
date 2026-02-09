from __future__ import annotations

from typing import Iterable

ROWS = 6
COLS = 36
ROW_LABELS = "ABCDEF"


class Pixel:
    """Immutable (row, col) coordinate. Used as set element and dict key."""

    __slots__ = ("_row", "_col")

    def __init__(self, row: int, col: int) -> None:
        if not (0 <= row < ROWS and 0 <= col < COLS):
            raise ValueError(f"Pixel ({row}, {col}) out of bounds (0-{ROWS-1}, 0-{COLS-1})")
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    @classmethod
    def from_string(cls, coordinate: str) -> Pixel:
        """Parse 'A5' -> Pixel(0, 5), 'F35' -> Pixel(5, 35)."""
        if len(coordinate) < 2:
            raise ValueError(f"Coordinate too short: '{coordinate}'")

        row_letter = coordinate[0].upper()
        if row_letter not in ROW_LABELS:
            raise ValueError(f"Invalid row '{row_letter}', must be A-F")

        try:
            col = int(coordinate[1:])
        except ValueError:
            raise ValueError(f"Invalid column in '{coordinate}'")

        row = ROW_LABELS.index(row_letter)
        return cls(row, col)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pixel):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        return hash((self._row, self._col))

    def __repr__(self) -> str:
        return f"Pixel({self._row}, {self._col})"

    def __str__(self) -> str:
        return f"{ROW_LABELS[self._row]}{self._col}"


class View:
    """6×36 pixel grid. Stores only active (on) pixels for memory efficiency."""

    def __init__(self, pixels: Iterable[Pixel] | None = None) -> None:
        self._active_pixels: set[Pixel] = set(pixels) if pixels else set()

    @classmethod
    def from_pixel_coordinates(cls, coordinate_sequence: str) -> View:
        """Parse 'A0A1B5F35' into View with those pixels on."""
        pixels = []
        current_token = []

        for char in coordinate_sequence:
            if char.isalpha():
                if current_token:
                    pixels.append(Pixel.from_string("".join(current_token)))
                current_token = [char]
            elif char.isdigit():
                if not current_token:
                    raise ValueError(f"Digit '{char}' without preceding row letter")
                current_token.append(char)
            elif char.isspace():
                continue
            else:
                raise ValueError(f"Invalid character '{char}'")

        if current_token:
            pixels.append(Pixel.from_string("".join(current_token)))

        return cls(pixels)

    @classmethod
    def parse(cls, user_input: str) -> View:
        """Auto-detect input format (coordinates vs text) and parse."""
        cleaned = user_input.replace(" ", "").upper()

        has_only_valid_chars = all(c in "ABCDEF0123456789" for c in cleaned)
        has_digits = any(c.isdigit() for c in cleaned)

        if has_only_valid_chars and has_digits:
            return cls.from_pixel_coordinates(cleaned)
        else:
            from fonts import render_text
            return render_text(cleaned)

    @property
    def active_pixels(self) -> frozenset[Pixel]:
        """Immutable snapshot prevents external mutation of internal state."""
        return frozenset(self._active_pixels)

    def render(self, on_char: str = "*", off_char: str = " ") -> str:
        """Convert grid to ASCII art string."""
        lines = []
        for row in range(ROWS):
            line = ""
            for col in range(COLS):
                pixel_is_on = Pixel(row, col) in self._active_pixels
                line += on_char if pixel_is_on else off_char
            lines.append(line)
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, View):
            return NotImplemented
        return self._active_pixels == other._active_pixels

    def __repr__(self) -> str:
        return f"View({len(self._active_pixels)} pixels)"
