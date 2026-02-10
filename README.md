# Electronic Sign Simulator

Interactive 6×36 pixel electronic sign simulator written in Go. Create views from pixel coordinates or text, render them as ASCII art, and manage them with a simple command-line interface.

## Requirements

- **Go 1.21+** (uses modern Go features)
- No external dependencies - uses only Go standard library

## Project Structure

```
electronic-sign/
├── main.go         # Entry point
├── sign.go         # Pixel and View types (core domain)
├── fonts.go        # Bitmap font rendering
├── cli.go          # Command-based interactive interface
├── sign_test.go    # Test suite
└── go.mod          # Go module definition
```

## Quick Start

```bash
# Build
go build

# Run
./electronic-sign
```

Or run directly:
```bash
go run .
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

Supported characters: **Full alphabet (A-Z), numbers (0-9), and common symbols** - all generated algorithmically!

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
go test -v
```

**Test Coverage:**
- Pixel creation, parsing, and value semantics
- View parsing (coordinates and text)
- Font rendering and validation
- Challenge specification compliance
- Boundary conditions and error handling

## Design Highlights

### Value Semantics

```go
pixel := Pixel{Row: 0, Col: 5}  // Immutable struct
// Comparable by value, usable as map key
```

Pixels are structs (not pointers) and use Go's value equality for comparison.

### Sparse Grid Representation

Views store only active (on) pixels in a map, not a full 2D array. Memory-efficient for partially lit signs.

### Auto-Detection Parsing

```go
ViewParse("A0A1B0")   // Detected as coordinates
ViewParse("ABC")      // Detected as text
```

### Comprehensive Documentation

All functions, types, and complex logic have detailed comments explaining:
- Purpose and behavior
- Design decisions and trade-offs
- Algorithm explanations
- Error conditions

## Coordinate System

- **Rows:** A-F (6 rows, top to bottom)
- **Columns:** 0-35 (36 columns, left to right)
- **Format:** Letter + number, e.g., `A0` (top-left), `F35` (bottom-right)

## Code Example

```go
package main

import "fmt"

func example() {
    // From coordinates
    view, _ := ViewFromPixelCoordinates("A5A6A8A9A13A14")
    fmt.Println(view.Render('*', ' '))

    // From text (centered)
    view, _ = ViewParse("ABC")
    fmt.Println(view.Render('*', ' '))
}
```

## Extending the Simulator

### Add New Characters

Characters are generated **algorithmically** using a stroke-based system (like segment displays). To add a new character, simply add a stroke combination to `getStrokes()`:

```go
case '@':
    return TopBar | BotBar | FullLeft | RightTopBar | MidBar
```

The system combines primitive strokes (TopBar, MidBar, BotBar, FullLeft, FullRight, Diagonals, Dot) to create any character. No bitmap patterns needed!

### Upgrade Path to Production

Current POC architecture supports easy upgrades:

- **Persistence:** Wrap map in Memory struct, add database backend
- **API:** Import as package in HTTP server
- **Package Structure:** Refactor into `sign/` and `fonts/` packages when team grows
- **Concurrent Access:** Add mutex to storedViews map

## Development

### Build

```bash
go build -o electronic-sign
```

### Test

```bash
go test                # Run tests
go test -v             # Verbose output
go test -cover         # With coverage
go test -bench=.       # Run benchmarks (if added)
```

### Format

```bash
go fmt ./...           # Format all Go files
```

### Lint

```bash
go vet ./...           # Run static analysis
```

## Technical Details

### Design Principles

- **Value semantics** - Pixels are structs, not pointers
- **Sparse representation** - Only store active pixels
- **Auto-detection** - Smart parsing of user input
- **No external dependencies** - Pure Go standard library
- **Comprehensive comments** - Enterprise-style documentation

### Performance Characteristics

- **Pixel creation:** O(1)
- **View rendering:** O(Rows × Cols) = O(216)
- **Coordinate parsing:** O(n) where n = input length
- **Pixel lookup:** O(1) map access
- **Memory:** O(active pixels), not O(total grid)

### Error Handling

All public functions return errors for invalid input:
- Boundary validation on pixel creation
- Format validation on parsing
- Character validation on text rendering

## License

MIT
