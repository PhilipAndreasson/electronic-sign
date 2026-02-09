# Electronic Sign Simulator

Interactive 6×36 pixel electronic sign simulator. Create views from pixel coordinates or text, render them as ASCII art, and manage them with a simple command-line interface.

## Requirements

- **Python 3.10+** (uses `X | Y` union syntax and pattern matching)
- No external dependencies

## Project Structure

```
electronic-sign/
├── main.py          # Entry point
├── sign.py          # Pixel and View classes (core domain)
├── fonts.py         # Bitmap font rendering
├── cli.py           # Command-based interactive interface
└── test_sign.py     # Test suite
```

## Quick Start

```bash
python3.13 main.py
```

## Usage

### Interactive Commands

```
>>> help
Commands:
  add              - Create and save a new view
  show <name>      - Display a saved view
  list             - List all saved views
  delete <name>    - Remove a saved view
  clear            - Delete all saved views
  exit             - Quit the application
```

### Creating Views

**Pixel Coordinates:**
```
>>> add
Enter pixels (A0A1B5) or text (ABC123): A0A1B0B1
```

**Text Rendering:**
```
>>> add
Enter pixels (A0A1B5) or text (ABC123): ABC123
```

Supported characters: `A B C 1 2 3`

### Managing Views

```
>>> list
Saved views:
  • greeting
  • test

>>> show greeting
── greeting ──
                  ***
                 *   *
                 *****
                 *   *
                 *   *
                 *   *

>>> delete greeting
✓ Deleted 'greeting'
```

## Running Tests

```bash
python3.13 -m unittest test_sign -v
```

**Test Coverage:**
- Pixel creation, parsing, and value semantics
- View parsing (coordinates and text)
- Font rendering and validation
- Challenge specification compliance
- Boundary conditions and error handling

## Design Highlights

### Immutable Value Objects

```python
pixel = Pixel(0, 5)
pixel.row  # 0 (read-only)
```

Pixels use `__slots__` for memory efficiency and implement proper equality/hashing for use in sets and dicts.

### Sparse Grid Representation

Views store only active (on) pixels in a set, not a full 2D array. Memory-efficient for partially lit signs.

### Auto-Detection Parsing

```python
View.parse("A0A1B0")   # Detected as coordinates
View.parse("ABC")      # Detected as text
```

### Self-Documenting Code

Variable names explain intent. Comments only where behavior isn't obvious from the code itself.

## Coordinate System

- **Rows:** A-F (6 rows, top to bottom)
- **Columns:** 0-35 (36 columns, left to right)
- **Format:** Letter + number, e.g., `A0` (top-left), `F35` (bottom-right)

## Example

```python
from sign import View

# From coordinates
view = View.from_pixel_coordinates("A5A6A8A9A13A14")
print(view.render())

# From text (centered)
view = View.parse("ABC")
print(view.render())
```

## Extending the Simulator

### Add New Characters

Edit `fonts.py` and add to the `GLYPHS` dictionary:

```python
GLYPHS: dict[str, list[str]] = {
    "A": [...],
    "D": [
        "**** ",
        "*   *",
        "*   *",
        "*   *",
        "*   *",
        "**** ",
    ],
}
```

No other changes needed. The renderer automatically supports new characters.

### Upgrade Path to Production

Current POC architecture supports easy upgrades:

- **Persistence:** Wrap dict in Memory class, add database backend
- **API:** Import `sign.py` and `fonts.py` directly in Flask/FastAPI
- **Testability:** Add dependency injection to CLI (already uses module-level storage)
- **Package Structure:** Split into `sign/` and `fonts/` packages when team grows

## License

MIT
