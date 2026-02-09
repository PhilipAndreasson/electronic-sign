import unittest

from fonts import render_text
from sign import COLS, ROWS, Pixel, View


class TestPixel(unittest.TestCase):
    """Core Pixel behavior: value semantics, parsing, validation."""

    def test_creation_and_properties(self):
        pixel = Pixel(0, 5)
        self.assertEqual(pixel.row, 0)
        self.assertEqual(pixel.col, 5)

    def test_from_string_parsing(self):
        pixel = Pixel.from_string("A5")
        self.assertEqual((pixel.row, pixel.col), (0, 5))

        pixel = Pixel.from_string("F35")
        self.assertEqual((pixel.row, pixel.col), (5, 35))

    def test_boundary_validation(self):
        with self.assertRaises(ValueError):
            Pixel(-1, 0)

        with self.assertRaises(ValueError):
            Pixel(0, -1)

        with self.assertRaises(ValueError):
            Pixel(ROWS, 0)

        with self.assertRaises(ValueError):
            Pixel(0, COLS)

    def test_value_semantics(self):
        p1 = Pixel(0, 0)
        p2 = Pixel(0, 0)
        p3 = Pixel(0, 1)

        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertEqual(hash(p1), hash(p2))
        self.assertNotEqual(hash(p1), hash(p3))

    def test_usable_in_sets(self):
        pixel_set = {Pixel(0, 0), Pixel(0, 1), Pixel(0, 0)}
        self.assertEqual(len(pixel_set), 2)


class TestView(unittest.TestCase):
    """Core View behavior: parsing, rendering, equality."""

    def test_empty_view_renders_blank(self):
        view = View()
        rendered = view.render()
        self.assertEqual(rendered.count(" "), ROWS * COLS)
        self.assertEqual(len(rendered.split("\n")), ROWS)

    def test_from_pixel_coordinates(self):
        view = View.from_pixel_coordinates("A0A1B0")
        self.assertEqual(len(view.active_pixels), 3)
        self.assertIn(Pixel(0, 0), view.active_pixels)
        self.assertIn(Pixel(0, 1), view.active_pixels)
        self.assertIn(Pixel(1, 0), view.active_pixels)

    def test_coordinate_parsing_handles_whitespace(self):
        view = View.from_pixel_coordinates("A0 A1 B0")
        self.assertEqual(len(view.active_pixels), 3)

    def test_coordinate_parsing_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            View.from_pixel_coordinates("5A")

    def test_auto_parse_detects_coordinates(self):
        view = View.parse("A0A1B0")
        self.assertEqual(len(view.active_pixels), 3)

    def test_auto_parse_detects_text(self):
        view = View.parse("ABC")
        self.assertGreater(len(view.active_pixels), 0)

    def test_render_customization(self):
        view = View.from_pixel_coordinates("A0")
        rendered = view.render(on_char="█", off_char="░")
        self.assertIn("█", rendered)
        self.assertIn("░", rendered)

    def test_active_pixels_immutable(self):
        view = View.from_pixel_coordinates("A0")
        pixels = view.active_pixels
        self.assertIsInstance(pixels, frozenset)

    def test_view_equality(self):
        v1 = View.from_pixel_coordinates("A0A1")
        v2 = View.from_pixel_coordinates("A1A0")
        v3 = View.from_pixel_coordinates("A0")

        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)


class TestFontRendering(unittest.TestCase):
    """Font rendering behavior: text conversion, validation."""

    def test_render_simple_text(self):
        view = render_text("A")
        self.assertGreater(len(view.active_pixels), 0)

    def test_render_multiple_characters(self):
        view = render_text("ABC")
        self.assertGreater(len(view.active_pixels), 0)

    def test_unsupported_character_raises(self):
        with self.assertRaises(ValueError):
            render_text("Z")

    def test_empty_text_raises(self):
        with self.assertRaises(ValueError):
            render_text("")

    def test_case_insensitive(self):
        v1 = render_text("abc")
        v2 = render_text("ABC")
        self.assertEqual(v1, v2)


class TestChallengeSpecification(unittest.TestCase):
    """Verify challenge example works correctly."""

    CHALLENGE_COORDINATES = "A5A6A8A9A13A14B5B9B13C5C6C7C8C9C13C14D5D9D13E5E6E8E9E13E14"

    def test_challenge_example_parses(self):
        view = View.from_pixel_coordinates(self.CHALLENGE_COORDINATES)
        self.assertEqual(len(view.active_pixels), 25)

    def test_challenge_renders_without_error(self):
        view = View.from_pixel_coordinates(self.CHALLENGE_COORDINATES)
        rendered = view.render()
        self.assertIsInstance(rendered, str)
        self.assertEqual(len(rendered.split("\n")), ROWS)


if __name__ == "__main__":
    unittest.main()
