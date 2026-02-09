#!/usr/bin/env python3
"""Entry point for the Electronic Sign Simulator."""

from sign.cli import SignCLI


def main() -> None:
    cli = SignCLI()
    cli.run()


if __name__ == "__main__":
    main()
