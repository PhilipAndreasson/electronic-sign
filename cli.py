from __future__ import annotations

import sys

from sign import View

_stored_views: dict[str, View] = {}


def run() -> None:
    """Interactive command-based sign simulator."""
    print("Electronic Sign Simulator")
    print("Type 'help' for available commands\n")

    while True:
        try:
            command = input(">>> ").strip()

            if not command:
                continue
            elif command == "help":
                _show_help()
            elif command == "exit":
                print("Goodbye!")
                break
            elif command == "add":
                _handle_add()
            elif command.startswith("show "):
                _handle_show(command[5:].strip())
            elif command == "list":
                _handle_list()
            elif command.startswith("delete "):
                _handle_delete(command[7:].strip())
            elif command == "clear":
                _handle_clear()
            else:
                print(f"Unknown command: '{command}' (type 'help' for options)")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def _show_help() -> None:
    print("Commands:")
    print("  add              - Create and save a new view")
    print("  show <name>      - Display a saved view")
    print("  list             - List all saved views")
    print("  delete <name>    - Remove a saved view")
    print("  clear            - Delete all saved views")
    print("  exit             - Quit the application")


def _handle_add() -> None:
    user_input = input("Enter pixels (A0A1B5) or text (ABC123): ").strip()
    if not user_input:
        print("No input provided")
        return

    try:
        view = View.parse(user_input)
        print("\nPreview:")
        print(view.render())

        view_name = input("\nName this view: ").strip()
        if not view_name:
            print("Name cannot be empty, view not saved")
            return

        _stored_views[view_name] = view
        print(f"✓ Saved as '{view_name}'")

    except ValueError as error:
        print(f"Error: {error}")


def _handle_show(view_name: str) -> None:
    if not view_name:
        print("Usage: show <name>")
        return

    if view_name not in _stored_views:
        print(f"View '{view_name}' not found")
        return

    print(f"\n── {view_name} ──")
    print(_stored_views[view_name].render())


def _handle_list() -> None:
    if not _stored_views:
        print("No saved views")
        return

    print("Saved views:")
    for view_name in _stored_views:
        print(f"  • {view_name}")


def _handle_delete(view_name: str) -> None:
    if not view_name:
        print("Usage: delete <name>")
        return

    if view_name not in _stored_views:
        print(f"View '{view_name}' not found")
        return

    del _stored_views[view_name]
    print(f"✓ Deleted '{view_name}'")


def _handle_clear() -> None:
    if not _stored_views:
        print("No views to clear")
        return

    view_count = len(_stored_views)
    confirmation = input(f"Delete all {view_count} view(s)? (y/N): ").strip().lower()

    if confirmation == "y":
        _stored_views.clear()
        print(f"✓ Cleared {view_count} view(s)")
    else:
        print("Cancelled")
