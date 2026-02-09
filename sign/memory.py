"""In-memory storage for electronic sign views."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterator

from sign.view import View


class Memory:
    """Ordered storage of named views.

    Views are stored with a unique string key (name) and maintain their
    insertion order.  Duplicate names overwrite the previous entry while
    preserving insertion position.
    """

    def __init__(self) -> None:
        self._views: OrderedDict[str, View] = OrderedDict()

    def save(self, name: str, view: View) -> None:
        """Store a view under the given name.

        If a view with the same name already exists it will be replaced.

        Args:
            name: A non-empty identifier for the view.
            view: The View to store.

        Raises:
            ValueError: If *name* is empty.
        """
        if not name.strip():
            raise ValueError("View name must not be empty")
        self._views[name] = view

    def get(self, name: str) -> View:
        """Retrieve a view by name.

        Args:
            name: Identifier of the stored view.

        Returns:
            The corresponding View.

        Raises:
            KeyError: If no view with that name exists.
        """
        if name not in self._views:
            raise KeyError(f"No view found with name '{name}'")
        return self._views[name]

    def delete(self, name: str) -> None:
        """Remove a view from memory.

        Args:
            name: Identifier of the view to delete.

        Raises:
            KeyError: If no view with that name exists.
        """
        if name not in self._views:
            raise KeyError(f"No view found with name '{name}'")
        del self._views[name]

    def clear(self) -> None:
        """Remove all views from memory."""
        self._views.clear()

    def list_names(self) -> list[str]:
        """Return the names of all stored views in insertion order."""
        return list(self._views.keys())

    def __len__(self) -> int:
        return len(self._views)

    def __contains__(self, name: str) -> bool:
        return name in self._views

    def __iter__(self) -> Iterator[tuple[str, View]]:
        """Iterate over (name, view) pairs in insertion order."""
        yield from self._views.items()

    def __repr__(self) -> str:
        return f"Memory(views={len(self._views)})"
