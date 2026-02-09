#!/usr/bin/env python3
"""Entry point for the Electronic Sign Simulator.

This minimal launcher imports and runs the CLI interface.
Keeping the entry point simple allows the CLI module to be
imported and tested independently.
"""

from cli import run

if __name__ == "__main__":
    run()
