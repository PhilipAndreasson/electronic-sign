"""Unit tests for sign.parser module."""

import unittest

from sign.parser import InputType, classify_input, parse_input


class TestClassifyInput(unittest.TestCase):
    """Test input classification heuristic."""

    def test_text_mode_abc(self):
        self.assertEqual(classify_input("ABC"), InputType.TEXT)

    def test_text_mode_123(self):
        self.assertEqual(classify_input("123"), InputType.TEXT)

    def test_text_mode_mixed(self):
        self.assertEqual(classify_input("ABC123"), InputType.TEXT)

    def test_coordinate_mode_with_D(self):
        self.assertEqual(classify_input("D0E1F2"), InputType.COORDINATES)

    def test_coordinate_mode_full_example(self):
        self.assertEqual(
            classify_input("A5A6D2D3E1F1"), InputType.COORDINATES
        )

    def test_empty_is_coordinates(self):
        # Will fail on parse, but classification defaults to COORDINATES.
        self.assertEqual(classify_input(""), InputType.COORDINATES)


class TestParseInput(unittest.TestCase):
    """Test end-to-end input parsing."""

    def test_coordinate_input(self):
        view = parse_input("A0A1B0B1")
        self.assertTrue(view.is_on(0, 0))
        self.assertTrue(view.is_on(0, 1))
        self.assertTrue(view.is_on(1, 0))
        self.assertTrue(view.is_on(1, 1))

    def test_text_input(self):
        view = parse_input("ABC123")
        # Should produce something with active pixels.
        self.assertGreater(len(view.active_pixels), 0)

    def test_invalid_input_raises(self):
        with self.assertRaises(ValueError):
            parse_input("G99")

    def test_whitespace_in_coordinates(self):
        view = parse_input("A0 A1")
        self.assertTrue(view.is_on(0, 0))
        self.assertTrue(view.is_on(0, 1))


if __name__ == "__main__":
    unittest.main()
