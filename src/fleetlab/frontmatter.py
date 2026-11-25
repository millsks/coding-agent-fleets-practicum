"""Read the YAML frontmatter at the top of agent and skill Markdown files.

Only the subset of YAML these files use is supported: ``key: value`` scalars, comma-separated or ``[a, b]`` lists,
``true``/``false``, integers, quoted strings, and ``#`` comments. Nested mappings (``hooks:``, ``mcpServers:``) are
kept as their raw indented text so checks can see that the key exists.
"""

from dataclasses import dataclass, field

LIST_KEYS = frozenset({"tools", "disallowedTools", "skills", "allowed-tools"})


class FrontmatterError(ValueError):
    """Raised when a file has no frontmatter or the frontmatter cannot be read."""


@dataclass
class Document:
    """A Markdown file split into frontmatter fields and body.

    Attributes:
        meta: Field names mapped to parsed values, in file order.
        body: Everything after the closing ``---``.
    """

    meta: dict[str, object] = field(default_factory=dict)
    body: str = ""


def _value(key: str, raw: str) -> object:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
    if key in LIST_KEYS:
        return [item.strip() for item in value.split(",") if item.strip()]
    if value in ("true", "false"):
        return value == "true"
    if value.lstrip("-").isdigit():
        return int(value)
    return value


def parse(text: str) -> Document:
    """Split Markdown text into frontmatter fields and body.

    Args:
        text: The whole file.

    Returns:
        The parsed document.

    Raises:
        FrontmatterError: If the frontmatter is missing, unterminated, or has a malformed or repeated key.
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("the file must start with a line containing only '---'")
    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        raise FrontmatterError("the frontmatter has no closing '---' line")

    doc = Document()
    current: str | None = None
    for number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[0] in " \t" or stripped.startswith("- "):
            if current is None:
                raise FrontmatterError(f"line {number}: indented line with no key above it")
            previous = doc.meta[current]
            if isinstance(previous, list) and stripped.startswith("- "):
                previous.append(stripped[2:].strip().strip("'\""))
            else:
                doc.meta[current] = f"{previous}\n{line}" if previous != "" else line
            continue
        key, sep, raw = stripped.partition(":")
        key = key.strip()
        if not sep or not key or " " in key:
            raise FrontmatterError(f"line {number}: expected 'key: value', got {stripped!r}")
        if key in doc.meta:
            raise FrontmatterError(f"line {number}: the key {key!r} appears twice")
        doc.meta[key] = _value(key, raw) if raw.strip() else ([] if key in LIST_KEYS else "")
        current = key
    doc.body = "\n".join(lines[end + 1 :]).strip("\n")
    return doc
