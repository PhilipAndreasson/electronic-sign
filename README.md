# Electronic Sign Simulator

An interactive application that simulates a 6×36 pixel electronic sign. Views
can be created from raw pixel coordinates or from character sequences (A, B, C,
1, 2, 3) rendered with a built-in bitmap font.

## Requirements

- **Python 3.10+** (uses `X | Y` union syntax and `match` compatible patterns)
- No external dependencies — the project uses only the Python standard library.

## Project Structure

```
electronic-sign/
├── main.py              # Application entry point
├── README.md
├── sign/                # Core domain package
│   ├── __init__.py
│   ├── pixel.py         # Pixel coordinate model
│   ├── view.py          # View (6×36 grid) model & coordinate parser
│   ├── memory.py        # Ordered in-memory view storage
│   ├── parser.py        # Input classification (coordinates vs text)
│   └── cli.py           # Interactive command-line interface
├── fonts/               # Bitmap font package
│   ├── __init__.py
│   ├── glyphs.py        # 5×6 glyph definitions for A-C, 1-3
│   └── renderer.py      # Text-to-View renderer
└── tests/               # Unit test suite
    ├── __init__.py
    ├── test_pixel.py
    ├── test_view.py
    ├── test_memory.py
    ├── test_renderer.py
    ├── test_parser.py
    └── test_cli.py
```

## How to Run

From the project root directory:

```bash
python main.py
```

This launches the interactive menu where you can:

1. **Add a new view** — enter pixel coordinates (e.g. `A0A1B5F35`) or
   characters (e.g. `ABC123`), preview it, and save with a name.
2. **Print a specific view** — display a stored view by name.
3. **Print all views** — display every view in memory.
4. **Delete a specific view** — remove a single view by name.
5. **Clear all views** — wipe the entire memory (with confirmation).
6. **Exit** — quit the application.

### Input Formats

**Pixel coordinates:** A letter A–F (row) followed by a number 0–35 (column),
concatenated without separators. Example:

```
A5A6A8A9A13A14...
```

**Character text:** A string of supported characters (A, B, C, 1, 2, 3) that
are rendered using the built-in bitmap font. Example:

```
ABC123
```

The application automatically detects which format you are using.

## How to Run Tests

```bash
python -m unittest discover -s tests -v
```

This discovers and runs all test files in the `tests/` directory. The suite
contains **80 tests** covering:

- Pixel creation, parsing, and validation
- View construction from coordinates and rendering
- Challenge specification examples (both coordinate and text)
- Memory CRUD operations and ordering
- Input classification heuristic
- CLI interaction flows (using dependency-injected I/O)

## Design Decisions

### Separation of Concerns

The codebase is split into clearly bounded packages:

- **`sign`** — core domain: `Pixel`, `View`, `Memory`, and input parsing.
- **`fonts`** — glyph definitions and the text renderer, decoupled from the
  core sign model so new fonts or characters can be added without touching
  domain code.
- **`tests`** — one test module per source module for clear traceability.

### Testability

The `SignCLI` class accepts `input_fn` and `output_fn` callables via
constructor injection, allowing the full CLI flow to be tested without
monkey-patching `sys.stdin`/`sys.stdout` or spawning subprocesses.

### Extensibility

- **Adding characters:** define a new entry in `fonts/glyphs.py` — the
  renderer and parser pick it up automatically.
- **Alternative UIs:** the domain layer (`View`, `Memory`, `parse_input`) has
  no dependency on the CLI, so a web or GUI front-end can reuse it directly.
- **Storage backends:** `Memory` could be swapped for a persistent
  implementation (e.g. SQLite) behind the same interface.

### Robustness

- All user input is validated with descriptive error messages.
- Invalid menu choices, empty names, and malformed coordinates are handled
  gracefully without crashing.
- `Ctrl+C` and `Ctrl+D` (EOF) exit cleanly.
