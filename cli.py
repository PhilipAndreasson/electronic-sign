"""Interactive command-line interface for the electronic sign simulator.

This module provides a command-based REPL (Read-Eval-Print Loop) that allows
users to create, view, and manage sign views through simple text commands.

Architecture:
- Module-level dict for storage (simple for POC, easy to upgrade to class)
- Command pattern for clean handler routing
- Graceful error handling with user-friendly messages
- Clean exit on Ctrl+C or Ctrl+D

Upgrade path:
When persistence is needed, wrap _stored_views in a Memory class with
database backend without changing the handler logic.
"""

from __future__ import annotations

import sys

from sign import View

# Module-level storage - maps view names to View objects
# Using dict instead of Memory class for POC simplicity
# Upgrade path: Replace with Memory class when persistence is needed
_stored_views: dict[str, View] = {}


def run() -> None:
    """Start the interactive command-line interface.

    Runs an infinite loop accepting commands until user exits.
    Handles keyboard interrupts gracefully to allow clean shutdown.
    """
    print("Electronic Sign Simulator")
    print("Type 'help' for available commands\n")

    while True:
        try:
            command = input(">>> ").strip()

            # Route command to appropriate handler
            if not command:
                # Ignore empty input, re-prompt
                continue
            elif command == "help":
                _show_help()
            elif command == "exit":
                print("Goodbye!")
                break
            elif command == "add":
                _handle_add()
            elif command.startswith("show "):
                # Extract view name after "show "
                _handle_show(command[5:].strip())
            elif command == "list":
                _handle_list()
            elif command.startswith("delete "):
                # Extract view name after "delete "
                _handle_delete(command[7:].strip())
            elif command == "clear":
                _handle_clear()
            else:
                print(f"Unknown command: '{command}' (type 'help' for options)")

        except (KeyboardInterrupt, EOFError):
            # Ctrl+C or Ctrl+D - exit gracefully
            print("\nGoodbye!")
            break


def _show_help() -> None:
    """Display available commands and their usage."""
    print("Commands:")
    print("  add              - Create and save a new view")
    print("  show <name>      - Display a saved view")
    print("  list             - List all saved views")
    print("  delete <name>    - Remove a saved view")
    print("  clear            - Delete all saved views")
    print("  exit             - Quit the application")


def _handle_add() -> None:
    """Create a new view from user input and save it with a name.

    Flow:
    1. Prompt for pixel coordinates or text
    2. Parse input (auto-detects format)
    3. Display preview for user verification
    4. Prompt for name
    5. Save to storage dict

    Handles parsing errors gracefully with user-friendly messages.
    """
    user_input = input("Enter pixels (A0A1B5) or text (ABC123): ").strip()

    if not user_input:
        print("No input provided")
        return

    try:
        # Parse handles auto-detection of format (coordinates vs text)
        view = View.parse(user_input)

        # Show preview so user can verify before saving
        print("\nPreview:")
        print(view.render())

        # Prompt for name to store under
        view_name = input("\nName this view: ").strip()
        if not view_name:
            print("Name cannot be empty, view not saved")
            return

        # Store in dict - simple assignment, no validation needed
        # (View object is already validated at this point)
        _stored_views[view_name] = view
        print(f"✓ Saved as '{view_name}'")

    except ValueError as error:
        # Parser or renderer raised ValueError - show user-friendly message
        print(f"Error: {error}")


def _handle_show(view_name: str) -> None:
    """Display a previously saved view by name.

    Args:
        view_name: Name of the view to display
    """
    if not view_name:
        print("Usage: show <name>")
        return

    # Check if view exists in storage
    if view_name not in _stored_views:
        print(f"View '{view_name}' not found")
        return

    # Display with header showing name
    print(f"\n── {view_name} ──")
    print(_stored_views[view_name].render())


def _handle_list() -> None:
    """List all saved view names.

    Shows a bulleted list if views exist, or a message if storage is empty.
    """
    if not _stored_views:
        print("No saved views")
        return

    print("Saved views:")
    for view_name in _stored_views:
        print(f"  • {view_name}")


def _handle_delete(view_name: str) -> None:
    """Remove a saved view by name.

    Args:
        view_name: Name of the view to delete
    """
    if not view_name:
        print("Usage: delete <name>")
        return

    if view_name not in _stored_views:
        print(f"View '{view_name}' not found")
        return

    # Remove from dict - Python dict handles deletion safely
    del _stored_views[view_name]
    print(f"✓ Deleted '{view_name}'")


def _handle_clear() -> None:
    """Delete all saved views after user confirmation.

    Requires explicit 'y' confirmation to prevent accidental data loss.
    """
    if not _stored_views:
        print("No views to clear")
        return

    view_count = len(_stored_views)

    # Confirm before destructive operation
    confirmation = input(f"Delete all {view_count} view(s)? (y/N): ").strip().lower()

    if confirmation == "y":
        _stored_views.clear()
        print(f"✓ Cleared {view_count} view(s)")
    else:
        print("Cancelled")
