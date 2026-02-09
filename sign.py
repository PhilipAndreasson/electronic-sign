"""Core domain models for the electronic sign simulator.

This module provides the fundamental building blocks:
- Pixel: Immutable coordinate representation
- View: Sparse grid of active pixels with rendering capability

Design decisions:
- Sparse representation (set of active pixels) for memory efficiency
- Immutable Pixel using __slots__ to reduce per-instance overhead
- Greedy tokenization for unambiguous parsing of multi-digit coordinates
"""

from __future__ import annotations

from typing import Iterable

# Display configuration - modify these to change sign dimensions
ROWS = 6
COLS = 36
ROW_LABELS = "ABCDEF"


class Pixel:
    """Immutable (row, col) coordinate for a single pixel on the sign.

    Pixels are value objects - equality is based on coordinate values,
    not object identity. They can be used as set elements and dict keys
    because they implement __eq__ and __hash__.

    Using __slots__ reduces memory overhead by ~40% compared to regular
    classes, important since we may create many Pixel instances.
    """

    __slots__ = ("_row", "_col")

    def __init__(self, row: int, col: int) -> None:
        """Create a new Pixel at the specified position.

        Args:
            row: Vertical position (0 = top)
            col: Horizontal position (0 = left)

        Raises:
            ValueError: If row or col is out of bounds
        """
        # Validate boundaries - fail fast if coordinates are invalid
        if not (0 <= row < ROWS and 0 <= col < COLS):
            raise ValueError(f"Pixel ({row}, {col}) out of bounds (0-{ROWS-1}, 0-{COLS-1})")

        # Store as private attributes to prevent external modification
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        """Vertical position (0-based, top to bottom)."""
        return self._row

    @property
    def col(self) -> int:
        """Horizontal position (0-based, left to right)."""
        return self._col

    @classmethod
    def from_string(cls, coordinate: str) -> Pixel:
        """Parse a coordinate string like 'A5' or 'F35' into a Pixel.

        Format: Letter (A-F for row) + number (0-35 for column)
        Examples: 'A0' = top-left, 'F35' = bottom-right

        Args:
            coordinate: String representation (e.g., 'B10')

        Returns:
            New Pixel instance at the parsed position

        Raises:
            ValueError: If format is invalid or coordinate is malformed
        """
        if len(coordinate) < 2:
            raise ValueError(f"Coordinate too short: '{coordinate}'")

        row_letter = coordinate[0].upper()
        if row_letter not in ROW_LABELS:
            raise ValueError(f"Invalid row '{row_letter}', must be A-F")

        # Parse column number - may be single or multi-digit
        try:
            col = int(coordinate[1:])
        except ValueError:
            raise ValueError(f"Invalid column in '{coordinate}'")

        # Convert letter to 0-based row index
        row = ROW_LABELS.index(row_letter)
        return cls(row, col)

    def __eq__(self, other: object) -> bool:
        """Compare pixels by value, not identity.

        Returns NotImplemented (not False) for non-Pixel objects to allow
        Python to try the reverse comparison and maintain proper protocol.
        """
        if not isinstance(other, Pixel):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        """Hash based on coordinates to allow use in sets and dicts."""
        return hash((self._row, self._col))

    def __repr__(self) -> str:
        """Developer-friendly representation showing numeric coordinates."""
        return f"Pixel({self._row}, {self._col})"

    def __str__(self) -> str:
        """User-friendly representation using letter-number format."""
        return f"{ROW_LABELS[self._row]}{self._col}"


class View:
    """Representation of a 6×36 pixel grid for the electronic sign.

    Uses sparse representation - only stores pixels that are ON (active).
    This is memory-efficient since most signs are partially lit.

    A fully lit sign would require 216 booleans, but a typical sign with
    20% active pixels only needs ~35 Pixel objects in a set.
    """

    def __init__(self, pixels: Iterable[Pixel] | None = None) -> None:
        """Create a View with the specified pixels turned on.

        Args:
            pixels: Iterable of Pixel objects to activate, or None for empty view
        """
        # Convert to set for O(1) membership testing during rendering
        self._active_pixels: set[Pixel] = set(pixels) if pixels else set()

    @classmethod
    def from_pixel_coordinates(cls, coordinate_sequence: str) -> View:
        """Parse a sequence of coordinates like 'A0A1B5F35' into a View.

        Uses greedy tokenization: each letter starts a new coordinate and
        consumes all following digits. This handles multi-digit columns
        unambiguously (e.g., 'B10' is one coordinate, not 'B1' + '0').

        Args:
            coordinate_sequence: Concatenated coordinates (e.g., 'A5B10C2')

        Returns:
            New View with specified pixels active

        Raises:
            ValueError: If sequence contains invalid characters or malformed coordinates
        """
        pixels = []
        current_token = []

        # Greedy tokenization: letter starts new token, digits extend it
        for char in coordinate_sequence:
            if char.isalpha():
                # Letter marks start of new coordinate - flush previous token
                if current_token:
                    pixels.append(Pixel.from_string("".join(current_token)))
                current_token = [char]
            elif char.isdigit():
                if not current_token:
                    raise ValueError(f"Digit '{char}' without preceding row letter")
                # Append digit to current coordinate (handles multi-digit columns)
                current_token.append(char)
            elif char.isspace():
                # Allow whitespace for readability, but ignore it
                continue
            else:
                raise ValueError(f"Invalid character '{char}'")

        # Don't forget the last token
        if current_token:
            pixels.append(Pixel.from_string("".join(current_token)))

        return cls(pixels)

    @classmethod
    def parse(cls, user_input: str) -> View:
        """Auto-detect input format and parse accordingly.

        Heuristic: If input contains only A-F and 0-9, AND has at least
        one digit, treat as pixel coordinates. Otherwise, treat as text
        to be rendered using the bitmap font.

        This allows users to type 'ABC' (renders as text) or 'A0B1C2'
        (creates pixels at those coordinates) without specifying format.

        Args:
            user_input: Raw input from user (coordinates or text)

        Returns:
            New View created from parsed input

        Raises:
            ValueError: If input is invalid for detected format
        """
        cleaned = user_input.replace(" ", "").upper()

        # Detection logic: coordinates must have digits, text may not
        has_only_valid_chars = all(c in "ABCDEF0123456789" for c in cleaned)
        has_digits = any(c.isdigit() for c in cleaned)

        if has_only_valid_chars and has_digits:
            # Looks like coordinates (e.g., 'A0B1C2')
            return cls.from_pixel_coordinates(cleaned)
        else:
            # Treat as text to render (e.g., 'ABC')
            from fonts import render_text
            return render_text(cleaned)

    @property
    def active_pixels(self) -> frozenset[Pixel]:
        """Get immutable snapshot of all active pixels.

        Returns frozenset instead of set to prevent callers from modifying
        internal state. This protects the View's invariants - pixels can
        only be changed through View's own methods.
        """
        return frozenset(self._active_pixels)

    def render(self, on_char: str = "*", off_char: str = " ") -> str:
        """Render the grid as a multi-line ASCII string.

        Iterates through all ROWS×COLS positions and checks membership
        in the active pixels set. Builds output row by row.

        Args:
            on_char: Character for active pixels (default '*')
            off_char: Character for inactive pixels (default ' ')

        Returns:
            Multi-line string with ROWS lines of COLS characters each
        """
        lines = []

        # Build output row by row
        for row in range(ROWS):
            line = ""
            # Check each position in this row
            for col in range(COLS):
                # O(1) set membership test
                pixel_is_on = Pixel(row, col) in self._active_pixels
                line += on_char if pixel_is_on else off_char
            lines.append(line)

        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        """Views are equal if they have the same active pixels.

        Set equality handles order independence - {A, B} == {B, A}.
        """
        if not isinstance(other, View):
            return NotImplemented
        return self._active_pixels == other._active_pixels

    def __repr__(self) -> str:
        """Developer-friendly representation showing pixel count."""
        return f"View({len(self._active_pixels)} pixels)"
