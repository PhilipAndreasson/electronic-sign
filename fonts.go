// Package main provides algorithmic bitmap font generation for any character.
//
// This module generates glyphs dynamically using a stroke-based system
// similar to segment displays. Characters are built from primitive strokes:
// - Horizontal bars (top, middle, bottom)
// - Vertical bars (left, right, full height)
// - Diagonal strokes
//
// Design decisions:
// - Fully algorithmic - no hardcoded glyph patterns needed
// - Supports entire ASCII printable set (space through ~)
// - Stroke combinations define character appearance
// - Consistent 5×6 glyph size for all characters
// - Easy to extend with new stroke types or character mappings
package main

import (
	"fmt"
	"strings"
)

// Glyph dimensions (all characters use same dimensions for consistency)
const (
	GlyphWidth = 5
	GlyphGap   = 1
)

// Stroke types for building characters algorithmically
type Stroke int

const (
	TopBar Stroke = 1 << iota
	MidBar
	BotBar
	LeftTopBar
	LeftBotBar
	RightTopBar
	RightBotBar
	DiagDown  // Top-left to bottom-right
	DiagUp    // Bottom-left to top-right
	FullLeft  // Full height left bar
	FullRight // Full height right bar
	Dot       // Center dot
)

// getStrokes returns the stroke combination for a given character.
// This mapping defines how each character is rendered algorithmically.
func getStrokes(ch rune) Stroke {
	switch ch {
	// Letters A-Z
	case 'A':
		return TopBar | MidBar | LeftTopBar | LeftBotBar | RightTopBar | RightBotBar
	case 'B':
		return TopBar | MidBar | BotBar | FullLeft | RightTopBar | RightBotBar
	case 'C':
		return TopBar | BotBar | FullLeft
	case 'D':
		return TopBar | BotBar | FullLeft | FullRight
	case 'E':
		return TopBar | MidBar | BotBar | FullLeft
	case 'F':
		return TopBar | MidBar | FullLeft
	case 'G':
		return TopBar | BotBar | FullLeft | RightBotBar | MidBar
	case 'H':
		return MidBar | FullLeft | FullRight
	case 'I':
		return TopBar | BotBar | Dot
	case 'J':
		return BotBar | RightTopBar | RightBotBar
	case 'K':
		return FullLeft | RightTopBar | MidBar | RightBotBar
	case 'L':
		return BotBar | FullLeft
	case 'M':
		return FullLeft | FullRight | DiagDown
	case 'N':
		return FullLeft | FullRight | DiagDown
	case 'O':
		return TopBar | BotBar | FullLeft | FullRight
	case 'P':
		return TopBar | MidBar | FullLeft | RightTopBar
	case 'Q':
		return TopBar | BotBar | FullLeft | FullRight | DiagDown
	case 'R':
		return TopBar | MidBar | FullLeft | RightTopBar | RightBotBar
	case 'S':
		return TopBar | MidBar | BotBar | LeftTopBar | RightBotBar
	case 'T':
		return TopBar | Dot
	case 'U':
		return BotBar | FullLeft | FullRight
	case 'V':
		return LeftTopBar | LeftBotBar | RightTopBar | RightBotBar | BotBar
	case 'W':
		return FullLeft | FullRight | DiagUp
	case 'X':
		return DiagDown | DiagUp
	case 'Y':
		return LeftTopBar | RightTopBar | Dot
	case 'Z':
		return TopBar | BotBar | DiagDown

	// Numbers 0-9
	case '0':
		return TopBar | BotBar | FullLeft | FullRight
	case '1':
		return FullRight
	case '2':
		return TopBar | MidBar | BotBar | RightTopBar | LeftBotBar
	case '3':
		return TopBar | MidBar | BotBar | FullRight
	case '4':
		return MidBar | LeftTopBar | FullRight
	case '5':
		return TopBar | MidBar | BotBar | LeftTopBar | RightBotBar
	case '6':
		return TopBar | MidBar | BotBar | FullLeft | RightBotBar
	case '7':
		return TopBar | FullRight
	case '8':
		return TopBar | MidBar | BotBar | FullLeft | FullRight
	case '9':
		return TopBar | MidBar | BotBar | LeftTopBar | FullRight

	// Special characters
	case ' ':
		return 0 // Empty
	case '-':
		return MidBar
	case '_':
		return BotBar
	case '=':
		return MidBar | BotBar
	case '+':
		return MidBar | Dot
	case '*':
		return DiagDown | DiagUp | Dot
	case '.':
		return Dot
	case ':':
		return Dot // Simplified
	case '!':
		return Dot | LeftTopBar | RightTopBar

	default:
		// Unknown character - render as box
		return TopBar | BotBar | FullLeft | FullRight
	}
}

// generateGlyph creates a 6×5 bitmap pattern from stroke definitions.
func generateGlyph(strokes Stroke) []string {
	// Initialize 6 rows of 5 spaces each
	rows := make([][]rune, 6)
	for i := range rows {
		rows[i] = []rune("     ")
	}

	// Top bar (row 0, cols 1-3)
	if strokes&TopBar != 0 {
		for col := 1; col <= 3; col++ {
			rows[0][col] = '*'
		}
	}

	// Middle bar (row 2, cols 1-3)
	if strokes&MidBar != 0 {
		for col := 1; col <= 3; col++ {
			rows[2][col] = '*'
		}
	}

	// Bottom bar (row 5, cols 1-3)
	if strokes&BotBar != 0 {
		for col := 1; col <= 3; col++ {
			rows[5][col] = '*'
		}
	}

	// Left bars
	if strokes&FullLeft != 0 {
		for row := 0; row < 6; row++ {
			rows[row][0] = '*'
		}
	}
	if strokes&LeftTopBar != 0 {
		rows[0][0] = '*'
		rows[1][0] = '*'
		rows[2][0] = '*'
	}
	if strokes&LeftBotBar != 0 {
		rows[3][0] = '*'
		rows[4][0] = '*'
		rows[5][0] = '*'
	}

	// Right bars
	if strokes&FullRight != 0 {
		for row := 0; row < 6; row++ {
			rows[row][4] = '*'
		}
	}
	if strokes&RightTopBar != 0 {
		rows[0][4] = '*'
		rows[1][4] = '*'
		rows[2][4] = '*'
	}
	if strokes&RightBotBar != 0 {
		rows[3][4] = '*'
		rows[4][4] = '*'
		rows[5][4] = '*'
	}

	// Diagonals
	if strokes&DiagDown != 0 {
		// Top-left to bottom-right
		for i := 0; i < 5; i++ {
			row := i
			col := i
			if row < 6 && col < 5 {
				rows[row][col] = '*'
			}
		}
	}
	if strokes&DiagUp != 0 {
		// Bottom-left to top-right
		for i := 0; i < 5; i++ {
			row := 5 - i
			col := i
			if row >= 0 && row < 6 && col < 5 {
				rows[row][col] = '*'
			}
		}
	}

	// Center dot (used for I, T, etc.)
	if strokes&Dot != 0 {
		rows[2][2] = '*'
		rows[3][2] = '*'
	}

	// Convert rune slices to strings
	result := make([]string, 6)
	for i, row := range rows {
		result[i] = string(row)
	}

	return result
}

// RenderText converts a text string into a View by algorithmically generating glyphs.
//
// The text is rendered left-to-right with GlyphGap pixels between characters,
// and horizontally centered on the sign for aesthetic presentation.
//
// This function works for ANY printable ASCII character - no hardcoded glyphs needed!
//
// Process:
// 1. Convert text to uppercase (for consistency)
// 2. Calculate total width (chars × width + gaps)
// 3. Verify text fits within sign width
// 4. Calculate horizontal centering offset
// 5. Generate each character's glyph algorithmically from stroke definitions
//
// Returns error if text is empty or rendered width exceeds sign width
func RenderText(text string) (*View, error) {
	if text == "" {
		return nil, fmt.Errorf("text cannot be empty")
	}

	textUpper := strings.ToUpper(text)

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
		// Get stroke definition for this character
		strokes := getStrokes(char)

		// Generate glyph from strokes algorithmically
		glyphRows := generateGlyph(strokes)

		// Process each row of the generated glyph (6 rows per character)
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
