// Package main provides interactive command-line interface for the electronic sign simulator.
//
// This module provides a command-based REPL (Read-Eval-Print Loop) that allows
// users to create, view, and manage sign views through simple text commands.
//
// Architecture:
// - Package-level map for storage (simple for POC, easy to upgrade to struct)
// - Command pattern for clean handler routing
// - Graceful error handling with user-friendly messages
// - Clean exit on Ctrl+C or Ctrl+D
//
// Upgrade path:
// When persistence is needed, wrap storedViews in a Memory struct with
// database backend without changing the handler logic.
package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// Package-level storage - maps view names to View pointers
// Using map instead of Memory struct for POC simplicity
// Upgrade path: Replace with Memory struct when persistence is needed
var storedViews = make(map[string]*View)

// Run starts the interactive command-line interface.
//
// Runs an infinite loop accepting commands until user exits.
// Handles EOF gracefully to allow clean shutdown.
func Run() {
	// Display welcome message with command menu
	fmt.Println("╔════════════════════════════════════════╗")
	fmt.Println("║     Electronic Sign Simulator         ║")
	fmt.Println("╠════════════════════════════════════════╣")
	fmt.Println("║  Commands:                             ║")
	fmt.Println("║    add              Create new view    ║")
	fmt.Println("║    show <name>      Display view       ║")
	fmt.Println("║    list             List all views     ║")
	fmt.Println("║    delete <name>    Remove view        ║")
	fmt.Println("║    clear            Delete all views   ║")
	fmt.Println("║    help             Show this menu     ║")
	fmt.Println("║    exit             Quit               ║")
	fmt.Println("╚════════════════════════════════════════╝")
	fmt.Println()

	scanner := bufio.NewScanner(os.Stdin)

	for {
		fmt.Print(">>> ")

		// Read command from user
		if !scanner.Scan() {
			// EOF (Ctrl+D) - exit gracefully
			fmt.Println("\nGoodbye!")
			break
		}

		command := strings.TrimSpace(scanner.Text())

		// Route command to appropriate handler
		if command == "" {
			// Ignore empty input, re-prompt
			continue
		}

		switch {
		case command == "help":
			showHelp()
		case command == "exit":
			fmt.Println("Goodbye!")
			return
		case command == "add":
			handleAdd(scanner)
		case strings.HasPrefix(command, "show "):
			// Extract view name after "show "
			handleShow(strings.TrimSpace(command[5:]))
		case command == "list":
			handleList()
		case strings.HasPrefix(command, "delete "):
			// Extract view name after "delete "
			handleDelete(strings.TrimSpace(command[7:]))
		case command == "clear":
			handleClear(scanner)
		default:
			fmt.Printf("Unknown command: '%s' (type 'help' for options)\n", command)
		}
	}
}

// showHelp displays available commands and their usage.
func showHelp() {
	fmt.Println("╔════════════════════════════════════════╗")
	fmt.Println("║  Commands:                             ║")
	fmt.Println("║    add              Create new view    ║")
	fmt.Println("║    show <name>      Display view       ║")
	fmt.Println("║    list             List all views     ║")
	fmt.Println("║    delete <name>    Remove view        ║")
	fmt.Println("║    clear            Delete all views   ║")
	fmt.Println("║    exit             Quit               ║")
	fmt.Println("╚════════════════════════════════════════╝")
}

// handleAdd creates a new view from user input and saves it with a name.
//
// Flow:
// 1. Prompt for pixel coordinates or text
// 2. Parse input (auto-detects format)
// 3. Display preview for user verification
// 4. Prompt for name
// 5. Save to storage map
//
// Handles parsing errors gracefully with user-friendly messages.
func handleAdd(scanner *bufio.Scanner) {
	fmt.Print("Enter pixels (A0A1B5) or text (ABC123): ")
	if !scanner.Scan() {
		return
	}

	userInput := strings.TrimSpace(scanner.Text())
	if userInput == "" {
		fmt.Println("No input provided")
		return
	}

	// Parse handles auto-detection of format (coordinates vs text)
	view, err := ViewParse(userInput)
	if err != nil {
		// Parser or renderer raised error - show user-friendly message
		fmt.Printf("Error: %v\n", err)
		return
	}

	// Show preview so user can verify before saving
	fmt.Println("\nPreview:")
	fmt.Println(view.Render('*', ' '))

	// Prompt for name to store under
	fmt.Print("\nName this view: ")
	if !scanner.Scan() {
		return
	}

	viewName := strings.TrimSpace(scanner.Text())
	if viewName == "" {
		fmt.Println("Name cannot be empty, view not saved")
		return
	}

	// Store in map - simple assignment, no validation needed
	// (View object is already validated at this point)
	storedViews[viewName] = view
	fmt.Printf("✓ Saved as '%s'\n", viewName)
}

// handleShow displays a previously saved view by name.
func handleShow(viewName string) {
	if viewName == "" {
		fmt.Println("Usage: show <name>")
		return
	}

	// Check if view exists in storage
	view, ok := storedViews[viewName]
	if !ok {
		fmt.Printf("View '%s' not found\n", viewName)
		return
	}

	// Display with header showing name
	fmt.Printf("\n── %s ──\n", viewName)
	fmt.Println(view.Render('*', ' '))
}

// handleList lists all saved view names.
//
// Shows a bulleted list if views exist, or a message if storage is empty.
func handleList() {
	if len(storedViews) == 0 {
		fmt.Println("No saved views")
		return
	}

	fmt.Println("Saved views:")
	for viewName := range storedViews {
		fmt.Printf("  • %s\n", viewName)
	}
}

// handleDelete removes a saved view by name.
func handleDelete(viewName string) {
	if viewName == "" {
		fmt.Println("Usage: delete <name>")
		return
	}

	if _, ok := storedViews[viewName]; !ok {
		fmt.Printf("View '%s' not found\n", viewName)
		return
	}

	// Remove from map - Go handles deletion safely
	delete(storedViews, viewName)
	fmt.Printf("✓ Deleted '%s'\n", viewName)
}

// handleClear deletes all saved views after user confirmation.
//
// Requires explicit 'y' confirmation to prevent accidental data loss.
func handleClear(scanner *bufio.Scanner) {
	if len(storedViews) == 0 {
		fmt.Println("No views to clear")
		return
	}

	viewCount := len(storedViews)

	// Confirm before destructive operation
	fmt.Printf("Delete all %d view(s)? (y/N): ", viewCount)
	if !scanner.Scan() {
		return
	}

	confirmation := strings.ToLower(strings.TrimSpace(scanner.Text()))

	if confirmation == "y" {
		storedViews = make(map[string]*View)
		fmt.Printf("✓ Cleared %d view(s)\n", viewCount)
	} else {
		fmt.Println("Cancelled")
	}
}
