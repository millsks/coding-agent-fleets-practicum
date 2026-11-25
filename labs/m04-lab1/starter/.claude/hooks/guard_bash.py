"""PreToolUse guard for Bash: block risky commands. See labs/m04-lab1/README.md."""

import json
import sys


def main() -> None:
    payload = json.load(sys.stdin)  # noqa: F841  (you'll use this)
    # TODO: block the commands in the README's table with exit code 2 and a helpful message on stderr.
    sys.exit(0)


if __name__ == "__main__":
    main()
