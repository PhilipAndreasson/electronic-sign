// Package main provides bitmap font system for rendering text on the electronic sign.
//
// This module provides glyph definitions and text-to-View rendering.
// Each character is defined as a 5×6 bitmap pattern that gets translated
// into Pixel coordinates.
//
// Design decisions:
// - Monospaced glyphs (all 5 columns wide) for consistent spacing
// - 1-pixel gap between characters for readability
// - Horizontal centering for aesthetic presentation
// - Easy extensibility - just add to glyphs map to support new characters
package main

import (
	"fmt"
	"sort"
	"strings"
)

// Glyph dimensions (all characters use same dimensions for consistency)
const (
	GlyphWidth = 5
	GlyphGap   = 1
)

// Bitmap font definition
// Each glyph is 6 rows × 5 columns, where '*' = pixel on, ' ' = pixel off
// To add new characters, simply add entries to this map
var glyphs = map[rune][]string{
	'A': {
		" *** ",
		"*   *",
		"*****",
		"*   *",
		"*   *",
		"*   *",
	},
	'B': {
		"**** ",
		"*   *",
		"**** ",
		"*   *",
		"*   *",
		"**** ",
	},
	'C': {
		" *** ",
		"*   *",
		"*    ",
		"*    ",
		"*   *",
		" *** ",
	},
	'1': {
		"  *  ",
		" **  ",
		"  *  ",
		"  *  ",
		"  *  ",
		" *** ",
	},
	'2': {
		" *** ",
		"*   *",
		"   * ",
		"  *  ",
		" *   ",
		"*****",
	},
	'3': {
		" *** ",
		"*   *",
		"  ** ",
		"    *",
		"*   *",
		" *** ",
	},
}

// RenderText converts a text string into a View by rendering each character as a bitmap glyph.
//
// The text is rendered left-to-right with GlyphGap pixels between characters,
// and horizontally centered on the sign for aesthetic presentation.
//
// Process:
// 1. Validate all characters are supported
// 2. Calculate total width (chars × width + gaps)
// 3. Verify text fits within sign width
// 4. Calculate horizontal centering offset
// 5. Render each character's glyph pattern into Pixel coordinates
//
// Returns error if text is empty, contains unsupported characters,
// or rendered width exceeds sign width
func RenderText(text string) (*View, error) {
	if text == "" {
		return nil, fmt.Errorf("text cannot be empty")
	}

	textUpper := strings.ToUpper(text)

	// Validate all characters are supported before attempting render
	var unsupportedChars []rune
	for _, ch := range textUpper {
		if _, ok := glyphs[ch]; !ok {
			unsupportedChars = append(unsupportedChars, ch)
		}
	}

	if len(unsupportedChars) > 0 {
		// Get sorted list of supported characters for error message
		var supported []rune
		for ch := range glyphs {
			supported = append(supported, ch)
		}
		sort.Slice(supported, func(i, j int) bool {
			return supported[i] < supported[j]
		})
		return nil, fmt.Errorf("unsupported characters %v. Available: %v", unsupportedChars, supported)
	}

	// Calculate total width: each char is GlyphWidth, with gaps between
	// Example: "ABC" = 5 + 1 + 5 + 1 + 5 = 17 columns
	totalWidth := len(textUpper)*GlyphWidth + (len(textUpper)-1)*GlyphGap

	// Ensure rendered text fits on sign
	if totalWidth > Cols {
		return nil, fmt.Errorf("text width %d exceeds sign width %d", totalWidth, Cols)
	}

	// Center text horizontally on the sign for better aesthetics
	// Example: 36-col sign with 17-col text → offset = (36-17)/2 = 9
	horizontalOffset := (Cols - totalWidth) / 2

	var pixels []Pixel
	currentCol := horizontalOffset

	// Render each character in sequence
	for _, char := range textUpper {
		glyphRows := glyphs[char]

		// Process each row of the glyph (6 rows per character)
		for rowIndex, rowPattern := range glyphRows {
			// Check each cell in the row (5 cells per row)
			for colOffset, cell := range rowPattern {
				// '*' indicates pixel should be on
				if cell != ' ' {
					p, _ := NewPixel(rowIndex, currentCol+colOffset)
					pixels = append(pixels, p)
				}
			}
		}

		// Move cursor right for next character (width + gap)
		currentCol += GlyphWidth + GlyphGap
	}

	return NewView(pixels), nil
}
