"""Summarise a Claude Code stream-json transcript.

Usage:
    python summarize_run.py TRANSCRIPT

See labs/m01-lab1/README.md for the exact output this script must print. Standard library only.
"""

import sys


def main(argv: list[str]) -> int:
    raise NotImplementedError("write the summariser")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
