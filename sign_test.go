// Test suite for the electronic sign simulator.
//
// This suite verifies core functionality across all components:
// - Pixel value semantics and boundary validation
// - View parsing, rendering, and equality
// - Font rendering and character validation
// - Challenge specification compliance
//
// Testing philosophy:
// - Test behaviors, not implementations (allows refactoring)
// - Focus on boundary conditions (off-by-one errors are common)
// - Verify value semantics (equality, hashing) for use in collections
// - Test integration points (challenge examples prove end-to-end flow)
package main

import (
	"strings"
	"testing"
)

// TestPixelCreation verifies Pixel stores coordinates correctly.
func TestPixelCreation(t *testing.T) {
	p, err := NewPixel(0, 5)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if p.Row != 0 || p.Col != 5 {
		t.Errorf("Expected (0, 5), got (%d, %d)", p.Row, p.Col)
	}
}

// TestPixelFromString verifies string coordinates are parsed correctly.
//
// Format: Letter (A-F) + number (0-35)
// 'A5' should parse to row=0, col=5
// 'F35' should parse to row=5, col=35
func TestPixelFromString(t *testing.T) {
	tests := []struct {
		input       string
		expectedRow int
		expectedCol int
	}{
		{"A5", 0, 5},
		{"F35", 5, 35},
		{"B10", 1, 10},
	}

	for _, tt := range tests {
		p, err := PixelFromString(tt.input)
		if err != nil {
			t.Errorf("PixelFromString(%s) returned error: %v", tt.input, err)
			continue
		}
		if p.Row != tt.expectedRow || p.Col != tt.expectedCol {
			t.Errorf("PixelFromString(%s) = (%d, %d), want (%d, %d)",
				tt.input, p.Row, p.Col, tt.expectedRow, tt.expectedCol)
		}
	}
}

// TestPixelBoundaryValidation verifies out-of-bounds coordinates are rejected.
//
// This catches off-by-one errors which are the most common bugs.
// Test both negative values and values at/beyond limits.
func TestPixelBoundaryValidation(t *testing.T) {
	tests := []struct {
		row int
		col int
	}{
		{-1, 0},  // Negative row
		{0, -1},  // Negative col
		{Rows, 0}, // Row at upper bound (6 should fail, valid is 0-5)
		{0, Cols}, // Col at upper bound (36 should fail, valid is 0-35)
	}

	for _, tt := range tests {
		_, err := NewPixel(tt.row, tt.col)
		if err == nil {
			t.Errorf("NewPixel(%d, %d) should have returned error", tt.row, tt.col)
		}
	}
}

// TestPixelValueSemantics verifies Pixels are compared by value, not identity.
//
// Two pixels with same coordinates should be equal even if
// they are different struct instances. Go compares structs by value.
func TestPixelValueSemantics(t *testing.T) {
	p1, _ := NewPixel(0, 0)
	p2, _ := NewPixel(0, 0)
	p3, _ := NewPixel(0, 1)

	// Same coordinates = equal
	if p1 != p2 {
		t.Errorf("Pixels with same coordinates should be equal")
	}

	// Different coordinates = not equal
	if p1 == p3 {
		t.Errorf("Pixels with different coordinates should not be equal")
	}
}

// TestPixelAsMapKey verifies Pixels can be used as map keys.
//
// Go uses value equality for struct keys.
// Adding the same coordinate twice should result in single entry.
func TestPixelAsMapKey(t *testing.T) {
	m := make(map[Pixel]bool)
	p1, _ := NewPixel(0, 0)
	p2, _ := NewPixel(0, 0) // Same coordinates as p1
	p3, _ := NewPixel(0, 1)

	m[p1] = true
	m[p2] = true // Should overwrite, not add
	m[p3] = true

	if len(m) != 2 {
		t.Errorf("Expected map length 2, got %d", len(m))
	}
}

// TestEmptyViewRendersBlank verifies empty view renders as all spaces.
func TestEmptyViewRendersBlank(t *testing.T) {
	view := NewView(nil)
	rendered := view.Render('*', ' ')

	// Should have Rows * Cols spaces
	spaceCount := strings.Count(rendered, " ")
	if spaceCount != Rows*Cols {
		t.Errorf("Expected %d spaces, got %d", Rows*Cols, spaceCount)
	}

	// Should have Rows lines
	lines := strings.Split(rendered, "\n")
	if len(lines) != Rows {
		t.Errorf("Expected %d lines, got %d", Rows, len(lines))
	}
}

// TestFromPixelCoordinates verifies coordinate sequence parsing.
func TestFromPixelCoordinates(t *testing.T) {
	view, err := ViewFromPixelCoordinates("A0A1B0")
	if err != nil {
		t.Fatalf("ViewFromPixelCoordinates returned error: %v", err)
	}

	// Should create exactly 3 active pixels
	activePixels := view.ActivePixels()
	if len(activePixels) != 3 {
		t.Errorf("Expected 3 active pixels, got %d", len(activePixels))
	}

	// Verify specific pixels are present
	expectedPixels := []Pixel{
		{Row: 0, Col: 0},
		{Row: 0, Col: 1},
		{Row: 1, Col: 0},
	}

	for _, expected := range expectedPixels {
		if !view.activePixels[expected] {
			t.Errorf("Expected pixel %v to be active", expected)
		}
	}
}

// TestCoordinateParsingWhitespace verifies whitespace is ignored.
func TestCoordinateParsingWhitespace(t *testing.T) {
	view, err := ViewFromPixelCoordinates("A0 A1 B0")
	if err != nil {
		t.Fatalf("ViewFromPixelCoordinates with whitespace returned error: %v", err)
	}

	// Should still create 3 pixels despite spaces
	activePixels := view.ActivePixels()
	if len(activePixels) != 3 {
		t.Errorf("Expected 3 active pixels, got %d", len(activePixels))
	}
}

// TestCoordinateParsingInvalid verifies malformed sequences are rejected.
//
// Example: '5A' has digit before letter, which violates format.
func TestCoordinateParsingInvalid(t *testing.T) {
	_, err := ViewFromPixelCoordinates("5A")
	if err == nil {
		t.Error("Expected error for malformed coordinate '5A'")
	}
}

// TestAutoParseCoordinates verifies auto-detection routes to coordinate parser.
//
// 'A0A1B0' contains only A-F and 0-9, and has digits, so should
// be parsed as coordinates not text.
func TestAutoParseCoordinates(t *testing.T) {
	view, err := ViewParse("A0A1B0")
	if err != nil {
		t.Fatalf("ViewParse returned error: %v", err)
	}

	activePixels := view.ActivePixels()
	if len(activePixels) != 3 {
		t.Errorf("Expected 3 active pixels, got %d", len(activePixels))
	}
}

// TestAutoParseText verifies auto-detection routes to text renderer.
//
// 'ABC' contains only letters (no digits), so should be rendered
// as text using bitmap font.
func TestAutoParseText(t *testing.T) {
	view, err := ViewParse("ABC")
	if err != nil {
		t.Fatalf("ViewParse returned error: %v", err)
	}

	// Text rendering should create multiple pixels (glyph patterns)
	activePixels := view.ActivePixels()
	if len(activePixels) == 0 {
		t.Error("Expected active pixels from text rendering")
	}
}

// TestRenderCustomization verifies render accepts custom characters.
func TestRenderCustomization(t *testing.T) {
	view, _ := ViewFromPixelCoordinates("A0")
	rendered := view.Render('█', '░')

	// Output should contain custom characters
	if !strings.Contains(rendered, "█") {
		t.Error("Expected '█' in rendered output")
	}
	if !strings.Contains(rendered, "░") {
		t.Error("Expected '░' in rendered output")
	}
}

// TestViewEquality verifies Views with same pixels are equal.
//
// Set equality is order-independent: {A, B} == {B, A}
func TestViewEquality(t *testing.T) {
	v1, _ := ViewFromPixelCoordinates("A0A1")
	v2, _ := ViewFromPixelCoordinates("A1A0") // Same pixels, different order
	v3, _ := ViewFromPixelCoordinates("A0")

	// Same pixels in different order should be equal
	if !v1.Equals(v2) {
		t.Error("Views with same pixels (different order) should be equal")
	}

	// Different pixel sets should not be equal
	if v1.Equals(v3) {
		t.Error("Views with different pixels should not be equal")
	}
}

// TestRenderSimpleText verifies single character renders successfully.
func TestRenderSimpleText(t *testing.T) {
	view, err := RenderText("A")
	if err != nil {
		t.Fatalf("RenderText returned error: %v", err)
	}

	// Should create pixels from glyph pattern
	activePixels := view.ActivePixels()
	if len(activePixels) == 0 {
		t.Error("Expected active pixels from glyph rendering")
	}
}

// TestRenderMultipleCharacters verifies multiple characters render with spacing.
func TestRenderMultipleCharacters(t *testing.T) {
	view, err := RenderText("ABC")
	if err != nil {
		t.Fatalf("RenderText returned error: %v", err)
	}

	// Should have pixels from all three glyphs
	activePixels := view.ActivePixels()
	if len(activePixels) == 0 {
		t.Error("Expected active pixels from multiple glyphs")
	}
}

// TestAllAlphabetSupported verifies full alphabet works.
func TestAllAlphabetSupported(t *testing.T) {
	// Test various letters and numbers work (sign width limits how many fit)
	tests := []string{"HELLO", "XYZ", "42"}
	for _, text := range tests {
		view, err := RenderText(text)
		if err != nil {
			t.Errorf("Should support '%s', got error: %v", text, err)
		}
		if view == nil {
			t.Errorf("Expected view for '%s'", text)
		}
	}
}

// TestEmptyTextError verifies empty string raises error.
func TestEmptyTextError(t *testing.T) {
	_, err := RenderText("")
	if err == nil {
		t.Error("Expected error for empty text")
	}
}

// TestCaseInsensitive verifies lowercase and uppercase render identically.
//
// Input is converted to uppercase before lookup.
func TestCaseInsensitive(t *testing.T) {
	v1, _ := RenderText("abc")
	v2, _ := RenderText("ABC")

	// Should produce identical Views
	if !v1.Equals(v2) {
		t.Error("Lowercase and uppercase should render identically")
	}
}

// TestChallengeExampleParses verifies challenge coordinate string works.
//
// Manual count of unique coordinates: 25 pixels
// (6 in row A, 3 in row B, 7 in row C, 3 in row D, 6 in row E)
func TestChallengeExampleParses(t *testing.T) {
	challengeCoords := "A5A6A8A9A13A14B5B9B13C5C6C7C8C9C13C14D5D9D13E5E6E8E9E13E14"
	view, err := ViewFromPixelCoordinates(challengeCoords)
	if err != nil {
		t.Fatalf("Challenge coordinates returned error: %v", err)
	}

	activePixels := view.ActivePixels()
	if len(activePixels) != 25 {
		t.Errorf("Expected 25 active pixels, got %d", len(activePixels))
	}
}

// TestChallengeRendersWithoutError verifies challenge renders successfully.
//
// Verifies:
// - No panics during rendering
// - Output has correct number of rows
func TestChallengeRendersWithoutError(t *testing.T) {
	challengeCoords := "A5A6A8A9A13A14B5B9B13C5C6C7C8C9C13C14D5D9D13E5E6E8E9E13E14"
	view, err := ViewFromPixelCoordinates(challengeCoords)
	if err != nil {
		t.Fatalf("Challenge coordinates returned error: %v", err)
	}

	rendered := view.Render('*', ' ')

	// Should have Rows lines
	lines := strings.Split(rendered, "\n")
	if len(lines) != Rows {
		t.Errorf("Expected %d lines, got %d", Rows, len(lines))
	}
}
