"""Checks for m02-lab1: the reviewer and test-writer definitions."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

import fleetlab
from fleetlab.agents import AgentSpec

SEEDED = Path(__file__).resolve().parent.parent / "seeded" / "bad-fix.patch"
BOUNDARY = re.compile(r"\b(never|do not|don't|must not)\b", re.IGNORECASE)
STOP = re.compile(r"\b(stop|hand back|hand it back|escalate)\b", re.IGNORECASE)


def load(workspace: Path, name: str) -> AgentSpec:
    path = workspace / ".claude" / "agents" / f"{name}.md"
    assert path.is_file(), f".claude/agents/{name}.md is missing"
    spec = fleetlab.load_agent(path)
    assert spec.problems == [], f"{name}.md: " + "; ".join(spec.problems)
    return spec


def common(spec: AgentSpec, name: str) -> None:
    assert spec.name == name
    tools = spec.tools
    assert tools is not None, "set tools explicitly; inheriting every tool is not least privilege"
    assert "Agent" not in tools, "this agent should not start subagents of its own"
    assert spec.meta.get("model"), "choose a model"
    turns = spec.meta.get("maxTurns")
    assert isinstance(turns, int) and 5 <= turns <= 40, "set maxTurns between 5 and 40"
    description = str(spec.meta.get("description", ""))
    assert "Use" in description or "use " in description, "the description should say when to use the agent"
    assert len(description) < 250, "keep the description under 250 characters"
    assert "TODO" not in spec.prompt and "TODO" not in description, "replace the TODOs"
    assert BOUNDARY.search(spec.prompt), "state a boundary: what the agent never does"
    assert STOP.search(spec.prompt), "say when the agent should stop or hand back"


def test_reviewer(workspace: Path) -> None:
    spec = load(workspace, "reviewer")
    common(spec, "reviewer")
    tools = spec.tools or set()
    assert {"Read", "Grep", "Glob"} <= tools, "the reviewer needs Read, Grep and Glob"
    assert not tools & fleetlab.WRITE_TOOLS, (
        f"the reviewer must not edit: remove {sorted(tools & fleetlab.WRITE_TOOLS)}"
    )
    assert re.search(r"\b(edit|change|modify)", spec.prompt, re.IGNORECASE), (
        "the boundary should be about not editing files"
    )


def test_reviewer_output_format(workspace: Path) -> None:
    prompt = load(workspace, "reviewer").prompt
    for token in ("BLOCKING", "NIT", "file:line", "VERDICT: approve", "VERDICT: changes requested"):
        assert token in prompt, f"the output format should include {token!r}"


def test_test_writer(workspace: Path) -> None:
    spec = load(workspace, "test-writer")
    common(spec, "test-writer")
    tools = spec.tools or set()
    assert "Read" in tools, "the test writer needs Read"
    assert tools & {"Write", "Edit"}, "the test writer needs Write or Edit to create tests"
    prompt = spec.prompt.lower()
    assert "tests/" in prompt, "keep the test writer to tests/"
    assert "acceptance criteria" in prompt, "work from the acceptance criteria, not the implementation"
    assert re.search(r"\bfail", prompt), "for a bug, write a test that fails before the fix"


def test_live_reviewer_blocks_seeded_fix(workspace: Path, claude_cli: str, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(workspace, repo)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

    git("init", "-q")
    git("add", "-A")
    git("-c", "user.name=lab", "-c", "user.email=lab@example.com", "commit", "-qm", "base")
    git("apply", str(SEEDED))
    done = subprocess.run(
        [
            claude_cli,
            "-p",
            "Use the reviewer subagent to review the uncommitted changes in this repository. "
            "Reply with the reviewer's findings and its final VERDICT line exactly.",
            "--allowedTools",
            "Read,Grep,Glob,Agent,Bash(git diff *),Bash(git status *)",
            "--max-turns",
            "30",
            "--output-format",
            "json",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-1000:]
    result = fleetlab.parse_stream(done.stdout).result or {}
    text = str(result.get("result", done.stdout))
    if "VERDICT:" not in text:
        pytest.fail(f"no VERDICT line in the review:\n{text[-1500:]}")
    assert "VERDICT: changes requested" in text, f"the seeded fix is wrong; the reviewer approved it:\n{text[-1500:]}"
