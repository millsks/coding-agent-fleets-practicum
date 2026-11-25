"""Checks for m03-lab1: AGENTS.md, CLAUDE.md, and the add-command skill."""

import re
import subprocess
from pathlib import Path

import pytest

import fleetlab

MAX_BYTES = 8 * 1024
MAX_LINES = 150
SECRET = re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}")


def sections(md: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in md.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return found


@pytest.fixture
def agents_md(workspace: Path) -> str:
    path = workspace / "AGENTS.md"
    assert path.is_file(), "AGENTS.md is missing"
    return path.read_text(encoding="utf-8")


def test_size_and_intro(agents_md: str) -> None:
    assert "TODO" not in agents_md, "replace the TODOs"
    assert len(agents_md.encode("utf-8")) <= MAX_BYTES, "keep AGENTS.md under 8 KiB"
    assert len(agents_md.splitlines()) <= MAX_LINES, f"keep AGENTS.md under {MAX_LINES} lines"
    intro = agents_md.split("## ", 1)[0]
    words = [w for line in intro.splitlines() if not line.startswith("#") for w in line.split()]
    assert len(words) >= 8, "start with a short paragraph describing the project"


def test_required_sections(agents_md: str) -> None:
    found = sections(agents_md)
    for name in ("commands", "map", "rules"):
        assert name in found, f"add a '## {name.title()}' section"


def test_commands_run(agents_md: str, workspace: Path) -> None:
    lines = [line for line in sections(agents_md).get("commands", []) if line.lstrip().startswith(("- ", "* "))]
    commands = [c for line in lines for c in re.findall(r"`([^`]+)`", line)]
    assert len(commands) >= 2, "list at least two commands, each in single backticks on a bullet line"
    assert any("pytest" in c for c in commands), "one command should run the tests with pytest"
    for command in commands:
        assert not command.startswith("pixi run"), f"`{command}`: give commands as they run inside the environment"
        assert not re.search(r"\bgit\s+push\b", command), f"`{command}` changes shared state; don't list it"
        done = subprocess.run(
            command, shell=True, cwd=workspace, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL
        )
        assert done.returncode == 0, f"`{command}` failed in a fresh workspace:\n{(done.stdout + done.stderr)[-1200:]}"


def test_map(agents_md: str) -> None:
    text = "\n".join(sections(agents_md).get("map", []))
    for path in ("shelf/", "tests/", "issues/"):
        assert path in text, f"the map should say what {path} holds"


def test_rules(agents_md: str) -> None:
    rules = [line for line in sections(agents_md).get("rules", []) if line.lstrip().startswith(("- ", "* "))]
    assert len(rules) >= 3, "give at least three bullet rules"
    assert any("test" in r.lower() for r in rules), "one rule should protect the tests"


def test_no_secrets(workspace: Path) -> None:
    for path in workspace.rglob("*.md"):
        assert not SECRET.search(path.read_text(encoding="utf-8")), f"{path.name} contains something that looks like a key"


def test_claude_md_imports_agents_md(workspace: Path) -> None:
    path = workspace / "CLAUDE.md"
    assert path.is_file(), "CLAUDE.md is missing"
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines and lines[0] == "@AGENTS.md", "the first non-empty line of CLAUDE.md must be @AGENTS.md"


def test_skill(workspace: Path) -> None:
    folder = workspace / ".claude" / "skills" / "add-command"
    skill = folder / "SKILL.md"
    assert skill.is_file(), ".claude/skills/add-command/SKILL.md is missing"
    text = skill.read_text(encoding="utf-8")
    problems = fleetlab.check_skill(text, "add-command")
    assert problems == [], "; ".join(problems)
    doc = fleetlab.parse(text)
    assert re.search(r"\b[Uu]se\b", str(doc.meta["description"])), "the description should say when to use the skill"
    for name in ("shelf/cli.py", "tests/test_cli.py"):
        assert name in doc.body, f"the procedure should name {name}"
    assert "reference.md" in doc.body, "link to reference.md so detail loads only when needed"
    reference = folder / "reference.md"
    assert reference.is_file() and reference.read_text(encoding="utf-8").strip(), "create a non-empty reference.md next to SKILL.md"
