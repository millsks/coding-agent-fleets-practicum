"""Stop hook: keep the agent working until the project's checks pass. See labs/m04-lab2/README.md."""

import json
import sys


def main() -> None:
    payload = json.load(sys.stdin)  # noqa: F841  (you'll use this)
    # TODO: implement the Stop gate described in the README.
    sys.exit(0)


if __name__ == "__main__":
    main()
