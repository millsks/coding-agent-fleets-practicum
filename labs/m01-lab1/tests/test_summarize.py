"""Checks for m01-lab1: summarize_run.py against recorded transcripts."""

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
KEYS = {"finished", "succeeded", "turns", "cost_usd", "tool_calls", "subagent_tool_calls", "failed_calls", "warnings"}


def summarize(workspace: Path, transcript: Path) -> dict[str, object]:
    script = workspace / "summarize_run.py"
    assert script.is_file(), "summarize_run.py is missing"
    done = subprocess.run([sys.executable, str(script), str(transcript)], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, f"exit {done.returncode}:\n{done.stderr[-1500:]}"
    try:
        data = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(f"stdout must be exactly one JSON object ({exc}):\n{done.stdout[:500]}")
    assert isinstance(data, dict), "print one JSON object"
    assert set(data) == KEYS, f"keys must be exactly {sorted(KEYS)}; got {sorted(data)}"
    return data


def test_standard_library_only(workspace: Path) -> None:
    tree = ast.parse((workspace / "summarize_run.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else []
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        for name in names:
            top = name.split(".")[0]
            assert top in sys.stdlib_module_names, f"import of {name!r}: use only the standard library"


def test_clean_run(workspace: Path) -> None:
    data = summarize(workspace, FIXTURES / "clean.jsonl")
    assert data["finished"] is True and data["succeeded"] is True
    assert data["turns"] == 6
    assert data["cost_usd"] == pytest.approx(0.0412)
    assert data["tool_calls"] == {"Grep": 1, "Read": 1, "Edit": 2, "Bash": 1}
    assert data["subagent_tool_calls"] == {}
    assert data["failed_calls"] == []
    assert data["warnings"] == [], "tests ran after the last edit, so there is nothing to warn about"


def test_premature_done(workspace: Path) -> None:
    data = summarize(workspace, FIXTURES / "premature.jsonl")
    assert data["succeeded"] is True, "the run itself succeeded; the warning says it isn't verified"
    assert data["warnings"] == ["unverified_edits"], "the tests ran before the last Write, not after it"


def test_doom_loop_with_subagent(workspace: Path) -> None:
    data = summarize(workspace, FIXTURES / "doom.jsonl")
    assert data["finished"] is True and data["succeeded"] is False, "subtype error_max_turns is not a success"
    assert data["tool_calls"] == {"Agent": 1, "Edit": 1, "Bash": 3}, "count only main-conversation calls here"
    assert data["subagent_tool_calls"] == {"Grep": 1, "Read": 1}, "calls with parent_tool_use_id belong here"
    assert len(data["failed_calls"]) == 3
    assert data["failed_calls"][0] == {"tool": "Bash", "input": {"command": "python -m pytest -q tests/test_cli.py"}}
    assert data["warnings"] == ["doom_loop"], (
        "pytest ran after the last edit (so it is verified) but failed three times in a row"
    )


def test_truncated_run(workspace: Path) -> None:
    data = summarize(workspace, FIXTURES / "truncated.jsonl")
    assert data["finished"] is False and data["succeeded"] is False
    assert data["turns"] == 0 and data["cost_usd"] == 0
    assert data["tool_calls"] == {"Read": 1, "Bash": 1}
    assert data["failed_calls"] == [{"tool": "Bash", "input": {"command": "git push origin main"}}]
    assert data["warnings"] == ["unfinished"], "skip stray non-JSON lines and report the missing result"


def test_missing_file(workspace: Path) -> None:
    done = subprocess.run(
        [sys.executable, str(workspace / "summarize_run.py"), str(workspace / "nope.jsonl")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert done.returncode == 2, "a missing transcript should exit 2"
    assert done.stderr.strip(), "explain the problem on stderr"


def test_live_run(workspace: Path, claude_cli: str, tmp_path: Path) -> None:
    transcript = tmp_path / "live.jsonl"
    with transcript.open("w", encoding="utf-8") as out:
        subprocess.run(
            [
                claude_cli,
                "-p",
                "Read shelf/store.py and summarise it in two sentences.",
                "--allowedTools",
                "Read",
                "--max-turns",
                "4",
                "--output-format",
                "stream-json",
                "--verbose",
            ],
            cwd=workspace,
            stdout=out,
            text=True,
            timeout=300,
            check=False,
        )
    data = summarize(workspace, transcript)
    assert data["finished"] is True, "the live run should reach its result line"
    assert data["tool_calls"].get("Read", 0) >= 1, "the agent should have read the file"  # type: ignore[union-attr]
