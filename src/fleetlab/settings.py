"""Read hook wiring from Claude Code settings (``.claude/settings.json``)."""

import re
from typing import Any

_PLAIN_MATCHER = re.compile(r"^[A-Za-z0-9_\-|, ]*$")


def matcher_matches(matcher: str | None, tool_name: str) -> bool:
    """Apply Claude Code's matcher rules to a tool name.

    * Empty, ``*``, or missing: matches every tool.
    * Only letters, digits, ``_``, ``-``, spaces, commas, and ``|``: an exact name, or a list split on ``|`` or ``,``.
    * Anything else: an unanchored regular expression, such as ``^Notebook`` or ``mcp__memory__.*``.

    Args:
        matcher: The matcher string from settings.
        tool_name: The tool about to run.

    Returns:
        Whether the hook group applies.
    """
    if matcher in (None, "", "*"):
        return True
    assert matcher is not None
    if _PLAIN_MATCHER.match(matcher):
        names = {part.strip() for part in re.split(r"[|,]", matcher) if part.strip()}
        return tool_name in names
    return re.search(matcher, tool_name) is not None


def hook_commands(settings: dict[str, Any], event: str, tool_name: str | None = None) -> list[str]:
    """List the command hooks that would run for an event (and tool, for tool events).

    Args:
        settings: Parsed ``settings.json``.
        event: Hook event such as ``PreToolUse`` or ``Stop``.
        tool_name: Tool name for tool events; ``None`` ignores matchers.

    Returns:
        The ``command`` strings in the order Claude Code would find them.
    """
    groups = settings.get("hooks", {}).get(event, [])
    commands: list[str] = []
    for group in groups if isinstance(groups, list) else []:
        if not isinstance(group, dict):
            continue
        if tool_name is not None and not matcher_matches(group.get("matcher"), tool_name):
            continue
        for hook in group.get("hooks", []):
            if isinstance(hook, dict) and hook.get("type", "command") == "command" and hook.get("command"):
                commands.append(str(hook["command"]))
    return commands
