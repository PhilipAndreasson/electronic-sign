"""Test suite for the electronic sign simulator.

This suite verifies core functionality across all components:
- Pixel value semantics and boundary validation
- View parsing, rendering, and equality
- Font rendering and character validation
- Challenge specification compliance

Testing philosophy:
- Test behaviors, not implementations (allows refactoring)
- Focus on boundary conditions (off-by-one errors are common)
- Verify value semantics (equality, hashing) for use in collections
- Test integration points (challenge examples prove end-to-end flow)
"""

import unittest

from fonts import render_text
from sign import COLS, ROWS, Pixel, View


class TestPixel(unittest.TestCase):
    """Test Pixel creation, parsing, validation, and value semantics.

    Pixels are value objects that must be:
    - Immutable (no modification after creation)
    - Comparable by value (not identity)
    - Hashable (for use in sets and dicts)
    - Boundary-validated (reject invalid coordinates)
    """

    def test_creation_and_properties(self):
        """Verify Pixel stores coordinates correctly and exposes via properties."""
        pixel = Pixel(0, 5)
        self.assertEqual(pixel.row, 0)
        self.assertEqual(pixel.col, 5)

    def test_from_string_parsing(self):
        """Verify string coordinates are parsed correctly.

        Format: Letter (A-F) + number (0-35)
        'A5' should parse to row=0, col=5
        'F35' should parse to row=5, col=35
        """
        pixel = Pixel.from_string("A5")
        self.assertEqual((pixel.row, pixel.col), (0, 5))

        pixel = Pixel.from_string("F35")
        self.assertEqual((pixel.row, pixel.col), (5, 35))

    def test_boundary_validation(self):
        """Verify out-of-bounds coordinates are rejected.

        This catches off-by-one errors which are the most common bugs.
        Test both negative values and values at/beyond limits.
        """
        # Negative row should raise
        with self.assertRaises(ValueError):
            Pixel(-1, 0)

        # Negative col should raise
        with self.assertRaises(ValueError):
            Pixel(0, -1)

        # Row at upper bound (6) should raise (valid range is 0-5)
        with self.assertRaises(ValueError):
            Pixel(ROWS, 0)

        # Col at upper bound (36) should raise (valid range is 0-35)
        with self.assertRaises(ValueError):
            Pixel(0, COLS)

    def test_value_semantics(self):
        """Verify Pixels are compared by value, not identity.

        Two pixels with same coordinates should be equal even if
        they are different objects. Hash should also match to allow
        proper behavior in sets and dicts.
        """
        p1 = Pixel(0, 0)
        p2 = Pixel(0, 0)
        p3 = Pixel(0, 1)

        # Same coordinates = equal (even though different objects)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)

        # Equal objects must have equal hashes
        self.assertEqual(hash(p1), hash(p2))
        # Different coordinates should (usually) have different hashes
        self.assertNotEqual(hash(p1), hash(p3))

    def test_usable_in_sets(self):
        """Verify Pixels can be used in sets with proper deduplication.

        Sets use hash and equality to determine uniqueness.
        Adding the same coordinate twice should result in single entry.
        """
        pixel_set = {Pixel(0, 0), Pixel(0, 1), Pixel(0, 0)}
        # Third pixel is duplicate of first, set should have 2 elements
        self.assertEqual(len(pixel_set), 2)


class TestView(unittest.TestCase):
    """Test View creation, parsing, rendering, and equality.

    Views use sparse representation (set of active pixels).
    Tests verify:
    - Empty views render correctly
    - Coordinate parsing handles various formats
    - Auto-detection selects correct parser
    - Rendering produces correct ASCII output
    - Immutability of active_pixels snapshot
    """

    def test_empty_view_renders_blank(self):
        """Empty view should render as all spaces."""
        view = View()
        rendered = view.render()

        # Should have ROWS * COLS spaces
        self.assertEqual(rendered.count(" "), ROWS * COLS)

        # Should have ROWS lines
        self.assertEqual(len(rendered.split("\n")), ROWS)

    def test_from_pixel_coordinates(self):
        """Verify coordinate sequence parsing creates correct pixels."""
        view = View.from_pixel_coordinates("A0A1B0")

        # Should create exactly 3 active pixels
        self.assertEqual(len(view.active_pixels), 3)

        # Verify specific pixels are present
        self.assertIn(Pixel(0, 0), view.active_pixels)
        self.assertIn(Pixel(0, 1), view.active_pixels)
        self.assertIn(Pixel(1, 0), view.active_pixels)

    def test_coordinate_parsing_handles_whitespace(self):
        """Whitespace between coordinates should be ignored for readability."""
        view = View.from_pixel_coordinates("A0 A1 B0")
        # Should still create 3 pixels despite spaces
        self.assertEqual(len(view.active_pixels), 3)

    def test_coordinate_parsing_rejects_invalid_input(self):
        """Malformed coordinate sequences should raise ValueError.

        Example: '5A' has digit before letter, which violates format.
        """
        with self.assertRaises(ValueError):
            View.from_pixel_coordinates("5A")

    def test_auto_parse_detects_coordinates(self):
        """Auto-detection should route to coordinate parser when digits present.

        'A0A1B0' contains only A-F and 0-9, and has digits, so should
        be parsed as coordinates not text.
        """
        view = View.parse("A0A1B0")
        self.assertEqual(len(view.active_pixels), 3)

    def test_auto_parse_detects_text(self):
        """Auto-detection should route to text renderer when no digits.

        'ABC' contains only letters (no digits), so should be rendered
        as text using bitmap font.
        """
        view = View.parse("ABC")
        # Text rendering should create multiple pixels (glyph patterns)
        self.assertGreater(len(view.active_pixels), 0)

    def test_render_customization(self):
        """Render should accept custom characters for on/off pixels."""
        view = View.from_pixel_coordinates("A0")
        rendered = view.render(on_char="█", off_char="░")

        # Output should contain custom characters
        self.assertIn("█", rendered)
        self.assertIn("░", rendered)

    def test_active_pixels_immutable(self):
        """active_pixels property should return frozenset to prevent mutation.

        This protects View's internal state from external modification.
        """
        view = View.from_pixel_coordinates("A0")
        pixels = view.active_pixels

        # Should be frozenset, not mutable set
        self.assertIsInstance(pixels, frozenset)

    def test_view_equality(self):
        """Views with same active pixels should be equal regardless of order.

        Set equality is order-independent: {A, B} == {B, A}
        """
        v1 = View.from_pixel_coordinates("A0A1")
        v2 = View.from_pixel_coordinates("A1A0")  # Same pixels, different order
        v3 = View.from_pixel_coordinates("A0")

        # Same pixels in different order should be equal
        self.assertEqual(v1, v2)
        # Different pixel sets should not be equal
        self.assertNotEqual(v1, v3)


class TestFontRendering(unittest.TestCase):
    """Test text-to-View rendering using bitmap fonts.

    Verifies:
    - Character validation (supported vs unsupported)
    - Case insensitivity
    - Empty text handling
    - Successful rendering of valid text
    """

    def test_render_simple_text(self):
        """Single character should render successfully."""
        view = render_text("A")
        # Should create pixels from glyph pattern
        self.assertGreater(len(view.active_pixels), 0)

    def test_render_multiple_characters(self):
        """Multiple characters should render with spacing."""
        view = render_text("ABC")
        # Should have pixels from all three glyphs
        self.assertGreater(len(view.active_pixels), 0)

    def test_unsupported_character_raises(self):
        """Characters not in GLYPHS dict should raise ValueError."""
        with self.assertRaises(ValueError):
            render_text("Z")

    def test_empty_text_raises(self):
        """Empty string should raise ValueError."""
        with self.assertRaises(ValueError):
            render_text("")

    def test_case_insensitive(self):
        """Lowercase and uppercase should render identically.

        Input is converted to uppercase before lookup.
        """
        v1 = render_text("abc")
        v2 = render_text("ABC")
        # Should produce identical Views
        self.assertEqual(v1, v2)


class TestChallengeSpecification(unittest.TestCase):
    """Verify challenge example coordinates work correctly.

    This tests the full end-to-end flow with the actual challenge input,
    ensuring the implementation matches the specification.
    """

    CHALLENGE_COORDINATES = "A5A6A8A9A13A14B5B9B13C5C6C7C8C9C13C14D5D9D13E5E6E8E9E13E14"

    def test_challenge_example_parses(self):
        """Challenge coordinate string should parse to correct pixel count.

        Manual count of unique coordinates in challenge string: 25 pixels
        (6 in row A, 3 in row B, 7 in row C, 3 in row D, 6 in row E)
        """
        view = View.from_pixel_coordinates(self.CHALLENGE_COORDINATES)
        self.assertEqual(len(view.active_pixels), 25)

    def test_challenge_renders_without_error(self):
        """Challenge example should render successfully to ASCII.

        Verifies:
        - No exceptions during rendering
        - Output is a string
        - Output has correct number of rows
        """
        view = View.from_pixel_coordinates(self.CHALLENGE_COORDINATES)
        rendered = view.render()

        # Should return string
        self.assertIsInstance(rendered, str)

        # Should have ROWS lines (6 for current spec)
        self.assertEqual(len(rendered.split("\n")), ROWS)


if __name__ == "__main__":
    unittest.main()
