"""Unit tests for sign.view module."""

import unittest

from sign.pixel import Pixel
from sign.view import View, _tokenize


class TestTokenize(unittest.TestCase):
    """Test the internal tokenizer used for coordinate parsing."""

    def test_simple_sequence(self):
        self.assertEqual(_tokenize("A0B1"), ["A0", "B1"])

    def test_two_digit_col(self):
        self.assertEqual(_tokenize("F35"), ["F35"])

    def test_mixed(self):
        tokens = _tokenize("A5A6B10F35")
        self.assertEqual(tokens, ["A5", "A6", "B10", "F35"])

    def test_whitespace_ignored(self):
        self.assertEqual(_tokenize("A0 B1"), ["A0", "B1"])

    def test_empty_string(self):
        self.assertEqual(_tokenize(""), [])

    def test_leading_digit_raises(self):
        with self.assertRaises(ValueError):
            _tokenize("0A")

    def test_special_char_raises(self):
        with self.assertRaises(ValueError):
            _tokenize("A0#B1")


class TestViewFromCoordinates(unittest.TestCase):
    """Test View construction from coordinate sequences."""

    def test_empty_sequence(self):
        v = View.from_pixel_coordinates("")
        self.assertEqual(len(v.active_pixels), 0)

    def test_single_pixel(self):
        v = View.from_pixel_coordinates("A0")
        self.assertTrue(v.is_on(0, 0))
        self.assertFalse(v.is_on(0, 1))

    def test_multiple_pixels(self):
        v = View.from_pixel_coordinates("A0A1F35")
        self.assertTrue(v.is_on(0, 0))
        self.assertTrue(v.is_on(0, 1))
        self.assertTrue(v.is_on(5, 35))
        self.assertEqual(len(v.active_pixels), 3)

    def test_duplicate_pixel_no_error(self):
        v = View.from_pixel_coordinates("A0A0A0")
        self.assertEqual(len(v.active_pixels), 1)

    def test_invalid_coordinate_raises(self):
        with self.assertRaises(ValueError):
            View.from_pixel_coordinates("G0")


class TestViewRender(unittest.TestCase):
    """Test view rendering to string."""

    def test_empty_view_renders_spaces(self):
        v = View()
        rendered = v.render()
        lines = rendered.split("\n")
        self.assertEqual(len(lines), 6)
        for line in lines:
            self.assertEqual(len(line), 36)
            self.assertTrue(all(c == " " for c in line))

    def test_single_pixel_rendered(self):
        v = View.from_pixel_coordinates("A0")
        rendered = v.render()
        self.assertEqual(rendered.split("\n")[0][0], "*")

    def test_custom_chars(self):
        v = View.from_pixel_coordinates("A0")
        rendered = v.render(on_char="X", off_char=".")
        self.assertEqual(rendered.split("\n")[0][0], "X")
        self.assertEqual(rendered.split("\n")[0][1], ".")


class TestViewEquality(unittest.TestCase):
    """Test View equality."""

    def test_equal_views(self):
        v1 = View.from_pixel_coordinates("A0B1")
        v2 = View.from_pixel_coordinates("B1A0")
        self.assertEqual(v1, v2)

    def test_unequal_views(self):
        v1 = View.from_pixel_coordinates("A0")
        v2 = View.from_pixel_coordinates("A1")
        self.assertNotEqual(v1, v2)


class TestChallengeExample(unittest.TestCase):
    """Verify the exact example given in the challenge specification."""

    EXAMPLE_INPUT = (
        "A5A6A8A9A13A14A16A17A20A21A22A23A24A30"
        "B4B5B6B9B10B12B13B16B17B19B20B29B31"
        "C3C4C5C6C10C11C12C16C17C20C21C28C32"
        "D2D3D5D6D10D11D12D16D17D22D23D27D28D29D33"
        "E1E2E3E4E5E6E9E10E12E13E16E17E23E24E26E30E34"
        "F1F2F5F6F8F9F13F14F16F17F19F20F21F22F23"
        "F25F26F27F28F29F30F31F32F33F34F35"
    )

    EXPECTED_OUTPUT = (
        "     ** **   ** **  *****     *     \n"
        "    ***  ** **  ** **        * *    \n"
        "   ****   ***   **  **      *   *   \n"
        "  ** **   ***   **    **   ***   *  \n"
        " ******  ** **  **     ** *   *   * \n"
        " **  ** **   ** ** ***** ***********"
    )

    def test_challenge_example(self):
        view = View.from_pixel_coordinates(self.EXAMPLE_INPUT)
        rendered = view.render()
        self.assertEqual(rendered, self.EXPECTED_OUTPUT)


if __name__ == "__main__":
    unittest.main()
