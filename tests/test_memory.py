"""Unit tests for sign.memory module."""

import unittest

from sign.memory import Memory
from sign.view import View


class TestMemorySaveAndGet(unittest.TestCase):
    """Test saving and retrieving views."""

    def setUp(self):
        self.memory = Memory()
        self.view = View.from_pixel_coordinates("A0A1")

    def test_save_and_get(self):
        self.memory.save("test", self.view)
        self.assertEqual(self.memory.get("test"), self.view)

    def test_overwrite(self):
        v2 = View.from_pixel_coordinates("B0")
        self.memory.save("test", self.view)
        self.memory.save("test", v2)
        self.assertEqual(self.memory.get("test"), v2)
        self.assertEqual(len(self.memory), 1)

    def test_get_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.memory.get("nope")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.memory.save("", self.view)

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            self.memory.save("   ", self.view)


class TestMemoryDelete(unittest.TestCase):
    """Test deleting views."""

    def setUp(self):
        self.memory = Memory()
        self.memory.save("v1", View.from_pixel_coordinates("A0"))
        self.memory.save("v2", View.from_pixel_coordinates("B0"))

    def test_delete(self):
        self.memory.delete("v1")
        self.assertEqual(len(self.memory), 1)
        self.assertNotIn("v1", self.memory)

    def test_delete_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.memory.delete("nope")


class TestMemoryClear(unittest.TestCase):
    """Test clearing all views."""

    def test_clear(self):
        mem = Memory()
        mem.save("v1", View.from_pixel_coordinates("A0"))
        mem.save("v2", View.from_pixel_coordinates("B0"))
        mem.clear()
        self.assertEqual(len(mem), 0)
        self.assertEqual(mem.list_names(), [])


class TestMemoryIteration(unittest.TestCase):
    """Test listing and iterating views."""

    def test_list_names_preserves_order(self):
        mem = Memory()
        mem.save("third", View())
        mem.save("first", View())
        mem.save("second", View())
        self.assertEqual(mem.list_names(), ["third", "first", "second"])

    def test_iteration(self):
        mem = Memory()
        v1 = View.from_pixel_coordinates("A0")
        v2 = View.from_pixel_coordinates("B0")
        mem.save("a", v1)
        mem.save("b", v2)
        items = list(mem)
        self.assertEqual(items, [("a", v1), ("b", v2)])

    def test_contains(self):
        mem = Memory()
        mem.save("x", View())
        self.assertIn("x", mem)
        self.assertNotIn("y", mem)


if __name__ == "__main__":
    unittest.main()
