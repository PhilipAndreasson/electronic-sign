"""Unit tests for fonts.glyphs and fonts.renderer modules."""

import unittest

from fonts.glyphs import GLYPH_WIDTH, get_glyph, is_supported_char
from fonts.renderer import render_text
from sign.pixel import COLS, ROWS


class TestGlyphs(unittest.TestCase):
    """Test glyph lookup and validation."""

    def test_supported_chars(self):
        for ch in "ABC123":
            self.assertTrue(is_supported_char(ch))

    def test_unsupported_chars(self):
        for ch in "XYZ789":
            self.assertFalse(is_supported_char(ch))

    def test_case_insensitive(self):
        self.assertTrue(is_supported_char("a"))
        self.assertTrue(is_supported_char("A"))

    def test_glyph_dimensions(self):
        for ch in "ABC123":
            glyph = get_glyph(ch)
            self.assertEqual(len(glyph), ROWS)
            for row in glyph:
                self.assertEqual(len(row), GLYPH_WIDTH)

    def test_unknown_glyph_raises(self):
        with self.assertRaises(ValueError):
            get_glyph("Z")


class TestRenderText(unittest.TestCase):
    """Test text-to-view rendering."""

    def test_single_char(self):
        view = render_text("A")
        rendered = view.render()
        lines = rendered.split("\n")
        self.assertEqual(len(lines), 6)
        for line in lines:
            self.assertEqual(len(line), COLS)

    def test_active_pixels_present(self):
        view = render_text("A")
        self.assertGreater(len(view.active_pixels), 0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            render_text("")

    def test_unsupported_char_raises(self):
        with self.assertRaises(ValueError):
            render_text("Z")

    def test_too_many_chars_raises(self):
        # 7 chars × 5 wide + 6 gaps = 41 > 36
        with self.assertRaises(ValueError):
            render_text("ABC1234")

    def test_six_chars_fits(self):
        # 6 chars × 5 wide + 5 gaps = 35 ≤ 36
        view = render_text("ABC123")
        self.assertIsNotNone(view)


class TestChallengeTextExample(unittest.TestCase):
    """Verify the ABC123 example from the challenge specification."""

    EXPECTED = (
        " ***  ****   ***    *    ***   ***  \n"
        "*   * *   * *   *  **   *   * *   * \n"
        "***** ****  *       *      *    **  \n"
        "*   * *   * *       *     *       * \n"
        "*   * *   * *   *   *    *    *   * \n"
        "*   * ****   ***   ***  *****  ***  "
    )

    def test_abc123(self):
        view = render_text("ABC123")
        rendered = view.render()
        self.assertEqual(rendered, self.EXPECTED)


if __name__ == "__main__":
    unittest.main()
