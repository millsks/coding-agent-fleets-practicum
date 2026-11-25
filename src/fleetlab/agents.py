"""Check Claude Code subagent definitions (``.claude/agents/<name>.md``).

Claude Code silently ignores frontmatter fields it does not recognise, so a typo such as ``maxturns`` fails quietly
at runtime. :func:`check_agent` makes those mistakes loud.
"""

from dataclasses import dataclass, field
from pathlib import Path

from fleetlab.frontmatter import FrontmatterError, parse

KNOWN_FIELDS = frozenset(
    {
        "name",
        "description",
        "tools",
        "disallowedTools",
        "model",
        "permissionMode",
        "isolation",
        "maxTurns",
        "autoCompactWindow",
        "skills",
        "mcpServers",
        "hooks",
        "memory",
        "background",
        "omitClaudeMd",
        "effort",
        "initialPrompt",
        "color",
    }
)
READ_ONLY_TOOLS = frozenset({"Read", "Grep", "Glob", "NotebookRead", "WebFetch", "WebSearch", "TodoWrite"})
WRITE_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
KNOWN_TOOLS = READ_ONLY_TOOLS | WRITE_TOOLS | {"Bash", "Agent", "Task", "Skill"}
MODELS = frozenset({"inherit", "opus", "sonnet", "haiku", "fable"})
PERMISSION_MODES = frozenset({"default", "manual", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"})
EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})


@dataclass
class AgentSpec:
    """A parsed subagent definition.

    Attributes:
        meta: Frontmatter fields.
        prompt: The body, which becomes the subagent's system prompt.
        problems: Everything :func:`check_agent` found wrong.
    """

    meta: dict[str, object] = field(default_factory=dict)
    prompt: str = ""
    problems: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        """The ``name`` field, or an empty string."""
        return str(self.meta.get("name", ""))

    @property
    def tools(self) -> set[str] | None:
        """The effective tool allowlist after ``disallowedTools``, or ``None`` when every tool is inherited."""
        listed = self.meta.get("tools")
        if not isinstance(listed, list):
            return None
        blocked = self.meta.get("disallowedTools") or []
        return {str(t) for t in listed} - {str(t) for t in blocked} if isinstance(blocked, list) else set(listed)

    def can_write(self) -> bool:
        """Tell whether the agent can change files: an edit tool, ``Bash``, or every tool inherited."""
        tools = self.tools
        if tools is None:
            blocked = self.meta.get("disallowedTools") or []
            return not (WRITE_TOOLS | {"Bash"}) <= set(blocked if isinstance(blocked, list) else [])
        return bool(tools & (WRITE_TOOLS | {"Bash"}))


def check_agent(text: str, filename: str | None = None) -> AgentSpec:
    """Parse a subagent file and record every problem found.

    Args:
        text: The file's contents.
        filename: The file name, such as ``reviewer.md``, to check ``name`` against.

    Returns:
        The parsed spec; ``spec.problems`` is empty when the file is valid.
    """
    try:
        doc = parse(text)
    except FrontmatterError as exc:
        return AgentSpec(problems=[str(exc)])
    spec = AgentSpec(meta=doc.meta, prompt=doc.body)
    problems = spec.problems
    meta = doc.meta

    for key in ("name", "description"):
        if not meta.get(key):
            problems.append(f"missing required field {key!r}")
    name = str(meta.get("name", ""))
    if name and (":" in name or len(name) > 256):
        problems.append("name must be at most 256 characters and contain no ':'")
    if filename and name and Path(filename).stem != name:
        problems.append(f"name {name!r} does not match the file name {Path(filename).name!r}")
    for key in sorted(set(meta) - KNOWN_FIELDS):
        problems.append(f"unknown field {key!r}: Claude Code would silently ignore it")
    for key in ("tools", "disallowedTools"):
        value = meta.get(key)
        for tool in value if isinstance(value, list) else []:
            if str(tool) not in KNOWN_TOOLS and not str(tool).startswith("mcp__") and "(" not in str(tool):
                problems.append(f"unknown tool {tool!r} in {key}")
    model = meta.get("model")
    if model is not None and str(model) not in MODELS and not str(model).startswith("claude-"):
        problems.append(f"unknown model {model!r}: use inherit, opus, sonnet, haiku, fable, or a full model ID")
    mode = meta.get("permissionMode")
    if mode is not None and mode not in PERMISSION_MODES:
        problems.append(f"unknown permissionMode {mode!r}")
    if meta.get("isolation") not in (None, "worktree"):
        problems.append("isolation must be 'worktree'")
    effort = meta.get("effort")
    if effort is not None and effort not in EFFORTS:
        problems.append(f"unknown effort {effort!r}")
    turns = meta.get("maxTurns")
    if turns is not None and (not isinstance(turns, int) or isinstance(turns, bool) or turns < 1):
        problems.append("maxTurns must be a positive whole number")
    if not doc.body.strip():
        problems.append("the body is empty: it becomes the subagent's system prompt")
    return spec


def load_agent(path: Path) -> AgentSpec:
    """Read and check a subagent file from disk.

    Args:
        path: Path to ``.claude/agents/<name>.md``.

    Returns:
        The checked spec.
    """
    return check_agent(path.read_text(encoding="utf-8"), filename=path.name)
