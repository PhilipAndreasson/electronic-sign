"""Interactive command-line interface for the electronic sign.

This module implements the interactive menu that lets users create, view,
and manage sign views stored in memory.
"""

from __future__ import annotations

import sys

from sign.memory import Memory
from sign.parser import parse_input


MENU = """
╔══════════════════════════════════════╗
║       Electronic Sign Manager        ║
╠══════════════════════════════════════╣
║  1. Add a new view                   ║
║  2. Print a specific view            ║
║  3. Print all views                  ║
║  4. Delete a specific view           ║
║  5. Clear all views                  ║
║  6. Exit                             ║
╚══════════════════════════════════════╝
"""


class SignCLI:
    """Interactive command-line controller for the electronic sign.

    Encapsulates the REPL loop and delegates to the domain layer
    (Memory, View, parser) for all business logic.
    """

    def __init__(
        self,
        memory: Memory | None = None,
        *,
        input_fn=input,
        output_fn=print,
    ) -> None:
        self._memory = memory or Memory()
        self._input = input_fn
        self._output = output_fn

    @property
    def memory(self) -> Memory:
        """Expose the memory for testability."""
        return self._memory

    # ── public entry point ──────────────────────────────────────────

    def run(self) -> None:
        """Start the interactive REPL loop."""
        self._output("Welcome to the Electronic Sign Simulator!")

        while True:
            self._output(MENU)
            choice = self._prompt("Select an option (1-6): ").strip()

            action = {
                "1": self._add_view,
                "2": self._print_view,
                "3": self._print_all_views,
                "4": self._delete_view,
                "5": self._clear_memory,
                "6": self._exit,
            }.get(choice)

            if action is None:
                self._output("Invalid option. Please enter a number 1-6.")
                continue

            action()

    # ── menu actions ────────────────────────────────────────────────

    def _add_view(self) -> None:
        """Prompt for pixel data and a name, then store the view."""
        self._output(
            "Enter pixel coordinates (e.g. A0A1B5F35) or "
            "characters (e.g. ABC123):"
        )
        raw = self._prompt("> ").strip()
        if not raw:
            self._output("No input provided. Returning to menu.")
            return

        try:
            view = parse_input(raw)
        except ValueError as exc:
            self._output(f"Error parsing input: {exc}")
            return

        self._output("\nPreview:")
        self._output(view.render())

        name = self._prompt("\nEnter a name for this view: ").strip()
        if not name:
            self._output("Name cannot be empty. View was not saved.")
            return

        try:
            self._memory.save(name, view)
        except ValueError as exc:
            self._output(f"Error saving view: {exc}")
            return

        self._output(f"View '{name}' saved successfully.")

    def _print_view(self) -> None:
        """Print a single stored view by name."""
        if not self._memory.list_names():
            self._output("Memory is empty.")
            return

        self._output(f"Stored views: {', '.join(self._memory.list_names())}")
        name = self._prompt("Enter the name of the view to print: ").strip()

        try:
            view = self._memory.get(name)
        except KeyError as exc:
            self._output(str(exc))
            return

        self._output(f"\n── {name} ──")
        self._output(view.render())

    def _print_all_views(self) -> None:
        """Print every stored view in insertion order."""
        if not self._memory.list_names():
            self._output("Memory is empty.")
            return

        for name, view in self._memory:
            self._output(f"\n── {name} ──")
            self._output(view.render())

    def _delete_view(self) -> None:
        """Delete a single stored view by name."""
        if not self._memory.list_names():
            self._output("Memory is empty.")
            return

        self._output(f"Stored views: {', '.join(self._memory.list_names())}")
        name = self._prompt("Enter the name of the view to delete: ").strip()

        try:
            self._memory.delete(name)
        except KeyError as exc:
            self._output(str(exc))
            return

        self._output(f"View '{name}' deleted.")

    def _clear_memory(self) -> None:
        """Clear all views from memory after confirmation."""
        if not self._memory.list_names():
            self._output("Memory is already empty.")
            return

        confirm = self._prompt(
            f"This will delete {len(self._memory)} view(s). "
            "Are you sure? (y/N): "
        ).strip().lower()

        if confirm == "y":
            self._memory.clear()
            self._output("Memory cleared.")
        else:
            self._output("Operation cancelled.")

    def _exit(self) -> None:
        """Exit the application."""
        self._output("Goodbye!")
        sys.exit(0)

    # ── helpers ─────────────────────────────────────────────────────

    def _prompt(self, message: str) -> str:
        """Read input from the user, handling EOF gracefully."""
        try:
            return self._input(message)
        except (EOFError, KeyboardInterrupt):
            self._output("\nGoodbye!")
            sys.exit(0)
