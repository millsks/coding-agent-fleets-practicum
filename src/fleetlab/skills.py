"""Check skills written in the open Agent Skills format (``<skills dir>/<name>/SKILL.md``)."""

import re

from fleetlab.frontmatter import FrontmatterError, parse

SKILL_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools", "disable-model-invocation"}
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_DESCRIPTION = 1024
MAX_BODY_LINES = 500


def check_skill(text: str, directory_name: str) -> list[str]:
    """Return every problem with a ``SKILL.md`` file.

    Args:
        text: The contents of ``SKILL.md``.
        directory_name: The name of the folder that holds it; the skill's ``name`` must match.

    Returns:
        Problems found; empty when the skill is valid.
    """
    try:
        doc = parse(text)
    except FrontmatterError as exc:
        return [str(exc)]
    problems: list[str] = []
    name = str(doc.meta.get("name", ""))
    description = str(doc.meta.get("description", ""))
    if not name:
        problems.append("missing required field 'name'")
    elif not NAME_PATTERN.match(name) or len(name) > 64:
        problems.append("name must be lowercase letters, digits, and single hyphens, at most 64 characters")
    if name and name != directory_name:
        problems.append(f"name {name!r} must match its folder name {directory_name!r}")
    if not description:
        problems.append("missing required field 'description'")
    elif len(description) > MAX_DESCRIPTION:
        problems.append(f"description is {len(description)} characters; the limit is {MAX_DESCRIPTION}")
    for key in sorted(set(doc.meta) - SKILL_FIELDS):
        problems.append(f"field {key!r} is not part of the Agent Skills format")
    if not doc.body.strip():
        problems.append("the body is empty: it holds the skill's instructions")
    elif len(doc.body.splitlines()) > MAX_BODY_LINES:
        problems.append(f"the body is over {MAX_BODY_LINES} lines; move detail into files the skill links to")
    return problems
