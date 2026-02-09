// Package main provides core domain models for the electronic sign simulator.
//
// This module provides the fundamental building blocks:
// - Pixel: Immutable coordinate representation
// - View: Sparse grid of active pixels with rendering capability
//
// Design decisions:
// - Sparse representation (map of active pixels) for memory efficiency
// - Value semantics for Pixel (comparable by value)
// - Greedy tokenization for unambiguous parsing of multi-digit coordinates
package main

import (
	"fmt"
	"strings"
	"unicode"
)

// Display configuration - modify these to change sign dimensions
const (
	Rows      = 6
	Cols      = 36
	RowLabels = "ABCDEF"
)

// Pixel represents an immutable (row, col) coordinate for a single pixel on the sign.
//
// Pixels are value objects - equality is based on coordinate values,
// not object identity. They can be used as map keys because Go compares
// structs by value.
type Pixel struct {
	Row int
	Col int
}

// NewPixel creates a new Pixel at the specified position.
//
// Args:
//   row: Vertical position (0 = top)
//   col: Horizontal position (0 = left)
//
// Returns error if row or col is out of bounds
func NewPixel(row, col int) (Pixel, error) {
	// Validate boundaries - fail fast if coordinates are invalid
	if row < 0 || row >= Rows {
		return Pixel{}, fmt.Errorf("pixel (%d, %d) out of bounds (0-%d, 0-%d)", row, col, Rows-1, Cols-1)
	}
	if col < 0 || col >= Cols {
		return Pixel{}, fmt.Errorf("pixel (%d, %d) out of bounds (0-%d, 0-%d)", row, col, Rows-1, Cols-1)
	}
	return Pixel{Row: row, Col: col}, nil
}

// FromString parses a coordinate string like 'A5' or 'F35' into a Pixel.
//
// Format: Letter (A-F for row) + number (0-35 for column)
// Examples: 'A0' = top-left, 'F35' = bottom-right
//
// Returns error if format is invalid or coordinate is malformed
func PixelFromString(coordinate string) (Pixel, error) {
	if len(coordinate) < 2 {
		return Pixel{}, fmt.Errorf("coordinate too short: '%s'", coordinate)
	}

	rowLetter := unicode.ToUpper(rune(coordinate[0]))
	rowIndex := strings.IndexRune(RowLabels, rowLetter)
	if rowIndex == -1 {
		return Pixel{}, fmt.Errorf("invalid row '%c', must be A-F", rowLetter)
	}

	// Parse column number - may be single or multi-digit
	var col int
	_, err := fmt.Sscanf(coordinate[1:], "%d", &col)
	if err != nil {
		return Pixel{}, fmt.Errorf("invalid column in '%s'", coordinate)
	}

	return NewPixel(rowIndex, col)
}

// String returns user-friendly representation using letter-number format
func (p Pixel) String() string {
	return fmt.Sprintf("%c%d", RowLabels[p.Row], p.Col)
}

// View represents a 6×36 pixel grid for the electronic sign.
//
// Uses sparse representation - only stores pixels that are ON (active).
// This is memory-efficient since most signs are partially lit.
//
// A fully lit sign would require 216 booleans, but a typical sign with
// 20% active pixels only needs ~35 Pixel entries in a map.
type View struct {
	// Map for O(1) membership testing during rendering
	activePixels map[Pixel]bool
}

// NewView creates a View with the specified pixels turned on.
func NewView(pixels []Pixel) *View {
	v := &View{
		activePixels: make(map[Pixel]bool),
	}
	for _, p := range pixels {
		v.activePixels[p] = true
	}
	return v
}

// FromPixelCoordinates parses a sequence of coordinates like 'A0A1B5F35' into a View.
//
// Uses greedy tokenization: each letter starts a new coordinate and
// consumes all following digits. This handles multi-digit columns
// unambiguously (e.g., 'B10' is one coordinate, not 'B1' + '0').
//
// Returns error if sequence contains invalid characters or malformed coordinates
func ViewFromPixelCoordinates(coordinateSequence string) (*View, error) {
	var pixels []Pixel
	var currentToken strings.Builder

	// Greedy tokenization: letter starts new token, digits extend it
	for _, char := range coordinateSequence {
		if unicode.IsLetter(char) {
			// Letter marks start of new coordinate - flush previous token
			if currentToken.Len() > 0 {
				p, err := PixelFromString(currentToken.String())
				if err != nil {
					return nil, err
				}
				pixels = append(pixels, p)
				currentToken.Reset()
			}
			currentToken.WriteRune(char)
		} else if unicode.IsDigit(char) {
			if currentToken.Len() == 0 {
				return nil, fmt.Errorf("digit '%c' without preceding row letter", char)
			}
			// Append digit to current coordinate (handles multi-digit columns)
			currentToken.WriteRune(char)
		} else if unicode.IsSpace(char) {
			// Allow whitespace for readability, but ignore it
			continue
		} else {
			return nil, fmt.Errorf("invalid character '%c'", char)
		}
	}

	// Don't forget the last token
	if currentToken.Len() > 0 {
		p, err := PixelFromString(currentToken.String())
		if err != nil {
			return nil, err
		}
		pixels = append(pixels, p)
	}

	return NewView(pixels), nil
}

// Parse auto-detects input format and parses accordingly.
//
// Heuristic: If input contains only A-F and 0-9, AND has at least
// one digit, treat as pixel coordinates. Otherwise, treat as text
// to be rendered using the bitmap font.
//
// This allows users to type 'ABC' (renders as text) or 'A0B1C2'
// (creates pixels at those coordinates) without specifying format.
//
// Returns error if input is invalid for detected format
func ViewParse(userInput string) (*View, error) {
	cleaned := strings.ToUpper(strings.ReplaceAll(userInput, " ", ""))

	// Detection logic: coordinates must have digits, text may not
	hasOnlyValidChars := true
	hasDigits := false

	for _, ch := range cleaned {
		if !strings.ContainsRune("ABCDEF0123456789", ch) {
			hasOnlyValidChars = false
			break
		}
		if unicode.IsDigit(ch) {
			hasDigits = true
		}
	}

	if hasOnlyValidChars && hasDigits {
		// Looks like coordinates (e.g., 'A0B1C2')
		return ViewFromPixelCoordinates(cleaned)
	}

	// Treat as text to render (e.g., 'ABC')
	return RenderText(cleaned)
}

// ActivePixels returns a slice of all active pixels.
func (v *View) ActivePixels() []Pixel {
	pixels := make([]Pixel, 0, len(v.activePixels))
	for p := range v.activePixels {
		pixels = append(pixels, p)
	}
	return pixels
}

// Render converts the grid to a multi-line ASCII string.
//
// Iterates through all Rows×Cols positions and checks membership
// in the active pixels map. Builds output row by row.
//
// Args:
//   onChar: Character for active pixels (default '*')
//   offChar: Character for inactive pixels (default ' ')
//
// Returns multi-line string with Rows lines of Cols characters each
func (v *View) Render(onChar, offChar rune) string {
	var lines []string

	// Build output row by row
	for row := 0; row < Rows; row++ {
		var line strings.Builder
		// Check each position in this row
		for col := 0; col < Cols; col++ {
			// O(1) map lookup
			if v.activePixels[Pixel{Row: row, Col: col}] {
				line.WriteRune(onChar)
			} else {
				line.WriteRune(offChar)
			}
		}
		lines = append(lines, line.String())
	}

	return strings.Join(lines, "\n")
}

// Equals checks if two Views have the same active pixels.
func (v *View) Equals(other *View) bool {
	if len(v.activePixels) != len(other.activePixels) {
		return false
	}
	for p := range v.activePixels {
		if !other.activePixels[p] {
			return false
		}
	}
	return true
}
