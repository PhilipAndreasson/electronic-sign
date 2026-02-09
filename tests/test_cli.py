"""Unit tests for sign.cli module.

Uses dependency-injected input/output functions to test the CLI
without actual user interaction.
"""

import unittest

from sign.cli import SignCLI
from sign.memory import Memory


class CLITestHelper:
    """Helper that provides fake input/output for CLI testing."""

    def __init__(self, inputs: list[str]) -> None:
        self._inputs = iter(inputs)
        self.outputs: list[str] = []

    def fake_input(self, _prompt: str = "") -> str:
        try:
            return next(self._inputs)
        except StopIteration:
            raise EOFError("No more test inputs")

    def fake_output(self, text: str = "") -> None:
        self.outputs.append(text)

    @property
    def all_output(self) -> str:
        return "\n".join(self.outputs)


class TestCLIAddView(unittest.TestCase):
    """Test adding views through the CLI."""

    def test_add_coordinate_view(self):
        helper = CLITestHelper([
            "1",       # menu choice
            "A0A1",    # pixel input
            "test_v",  # view name
            "6",       # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("test_v", cli.memory)
        self.assertIn("saved successfully", helper.all_output)

    def test_add_text_view(self):
        helper = CLITestHelper([
            "1",       # menu choice
            "ABC",     # text input
            "my_abc",  # view name
            "6",       # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("my_abc", cli.memory)

    def test_add_empty_input_aborts(self):
        helper = CLITestHelper([
            "1",   # menu choice
            "",    # empty input
            "6",   # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertEqual(len(cli.memory), 0)

    def test_add_empty_name_aborts(self):
        helper = CLITestHelper([
            "1",     # menu
            "A0A1",  # valid input
            "",      # empty name
            "6",     # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertEqual(len(cli.memory), 0)
        self.assertIn("Name cannot be empty", helper.all_output)


class TestCLIPrintView(unittest.TestCase):
    """Test printing specific views."""

    def test_print_existing_view(self):
        mem = Memory()
        from sign.view import View
        mem.save("hello", View.from_pixel_coordinates("A0"))

        helper = CLITestHelper([
            "2",       # print specific
            "hello",   # name
            "6",       # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("── hello ──", helper.all_output)

    def test_print_nonexistent_view(self):
        mem = Memory()
        mem.save("x", __import__("sign.view", fromlist=["View"]).View())

        helper = CLITestHelper([
            "2",      # print specific
            "nope",   # nonexistent name
            "6",      # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("No view found", helper.all_output)

    def test_print_empty_memory(self):
        helper = CLITestHelper([
            "2",  # print specific
            "6",  # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("Memory is empty", helper.all_output)


class TestCLIPrintAll(unittest.TestCase):
    """Test printing all views."""

    def test_print_all(self):
        mem = Memory()
        from sign.view import View
        mem.save("v1", View.from_pixel_coordinates("A0"))
        mem.save("v2", View.from_pixel_coordinates("B0"))

        helper = CLITestHelper([
            "3",  # print all
            "6",  # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("── v1 ──", helper.all_output)
        self.assertIn("── v2 ──", helper.all_output)


class TestCLIDeleteView(unittest.TestCase):
    """Test deleting views."""

    def test_delete_existing(self):
        mem = Memory()
        from sign.view import View
        mem.save("todel", View())

        helper = CLITestHelper([
            "4",       # delete
            "todel",   # name
            "6",       # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertNotIn("todel", cli.memory)
        self.assertIn("deleted", helper.all_output)


class TestCLIClearMemory(unittest.TestCase):
    """Test clearing memory."""

    def test_clear_confirmed(self):
        mem = Memory()
        from sign.view import View
        mem.save("v1", View())

        helper = CLITestHelper([
            "5",   # clear
            "y",   # confirm
            "6",   # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertEqual(len(cli.memory), 0)

    def test_clear_cancelled(self):
        mem = Memory()
        from sign.view import View
        mem.save("v1", View())

        helper = CLITestHelper([
            "5",   # clear
            "n",   # cancel
            "6",   # exit
        ])
        cli = SignCLI(memory=mem, input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertEqual(len(cli.memory), 1)


class TestCLIInvalidOption(unittest.TestCase):
    """Test invalid menu option handling."""

    def test_invalid_option(self):
        helper = CLITestHelper([
            "99",  # invalid
            "6",   # exit
        ])
        cli = SignCLI(input_fn=helper.fake_input, output_fn=helper.fake_output)
        with self.assertRaises(SystemExit):
            cli.run()

        self.assertIn("Invalid option", helper.all_output)


if __name__ == "__main__":
    unittest.main()
