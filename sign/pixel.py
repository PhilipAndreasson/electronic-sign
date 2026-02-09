"""Pixel coordinate representation for the electronic sign."""

from __future__ import annotations

ROWS = 6
COLS = 36

ROW_LABELS = "ABCDEF"


class Pixel:
    """Immutable representation of a single pixel coordinate on the sign.

    The vertical position is indicated by a letter (A-F) and the
    horizontal position by a number (0-35).

    Examples:
        >>> Pixel(0, 0)   # top-left, equivalent to "A0"
        Pixel(row=0, col=0)
        >>> Pixel.from_string("F35")  # bottom-right
        Pixel(row=5, col=35)
    """

    __slots__ = ("_row", "_col")

    def __init__(self, row: int, col: int) -> None:
        if not (0 <= row < ROWS):
            raise ValueError(f"Row must be 0-{ROWS - 1}, got {row}")
        if not (0 <= col < COLS):
            raise ValueError(f"Column must be 0-{COLS - 1}, got {col}")
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
        """Parse a pixel coordinate string like 'A0' or 'F35'.

        Args:
            coordinate: A string starting with a letter A-F followed by
                a number 0-35.

        Returns:
            A new Pixel instance.

        Raises:
            ValueError: If the coordinate string is malformed.
        """
        if len(coordinate) < 2:
            raise ValueError(f"Invalid coordinate: '{coordinate}'")

        letter = coordinate[0].upper()
        if letter not in ROW_LABELS:
            raise ValueError(
                f"Invalid row letter '{letter}'. Must be one of {ROW_LABELS}"
            )

        try:
            col = int(coordinate[1:])
        except ValueError:
            raise ValueError(
                f"Invalid column number in coordinate: '{coordinate}'"
            )

        row = ROW_LABELS.index(letter)
        return cls(row, col)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pixel):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        return hash((self._row, self._col))

    def __repr__(self) -> str:
        return f"Pixel(row={self._row}, col={self._col})"

    def __str__(self) -> str:
        return f"{ROW_LABELS[self._row]}{self._col}"
