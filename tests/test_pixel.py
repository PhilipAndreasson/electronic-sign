"""Unit tests for sign.pixel module."""

import unittest

from sign.pixel import COLS, ROWS, Pixel


class TestPixelCreation(unittest.TestCase):
    """Test basic Pixel construction and boundary checking."""

    def test_valid_pixel(self):
        p = Pixel(0, 0)
        self.assertEqual(p.row, 0)
        self.assertEqual(p.col, 0)

    def test_bottom_right(self):
        p = Pixel(ROWS - 1, COLS - 1)
        self.assertEqual(p.row, 5)
        self.assertEqual(p.col, 35)

    def test_negative_row_raises(self):
        with self.assertRaises(ValueError):
            Pixel(-1, 0)

    def test_row_too_large_raises(self):
        with self.assertRaises(ValueError):
            Pixel(ROWS, 0)

    def test_negative_col_raises(self):
        with self.assertRaises(ValueError):
            Pixel(0, -1)

    def test_col_too_large_raises(self):
        with self.assertRaises(ValueError):
            Pixel(0, COLS)


class TestPixelFromString(unittest.TestCase):
    """Test Pixel.from_string parsing."""

    def test_A0(self):
        p = Pixel.from_string("A0")
        self.assertEqual(p, Pixel(0, 0))

    def test_F35(self):
        p = Pixel.from_string("F35")
        self.assertEqual(p, Pixel(5, 35))

    def test_case_insensitive(self):
        self.assertEqual(Pixel.from_string("a0"), Pixel.from_string("A0"))

    def test_single_char_raises(self):
        with self.assertRaises(ValueError):
            Pixel.from_string("A")

    def test_invalid_letter_raises(self):
        with self.assertRaises(ValueError):
            Pixel.from_string("G0")

    def test_invalid_col_raises(self):
        with self.assertRaises(ValueError):
            Pixel.from_string("A36")

    def test_non_digit_suffix_raises(self):
        with self.assertRaises(ValueError):
            Pixel.from_string("Ax")


class TestPixelEquality(unittest.TestCase):
    """Test Pixel equality and hashing."""

    def test_equal_pixels(self):
        self.assertEqual(Pixel(1, 2), Pixel(1, 2))

    def test_unequal_pixels(self):
        self.assertNotEqual(Pixel(0, 0), Pixel(0, 1))

    def test_hashable(self):
        s = {Pixel(0, 0), Pixel(0, 0), Pixel(1, 1)}
        self.assertEqual(len(s), 2)

    def test_str(self):
        self.assertEqual(str(Pixel(0, 0)), "A0")
        self.assertEqual(str(Pixel(5, 35)), "F35")


if __name__ == "__main__":
    unittest.main()
