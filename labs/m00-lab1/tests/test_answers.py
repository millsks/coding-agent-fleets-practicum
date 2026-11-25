"""Checks for m00-lab1: every answer about shelf is verified against the code."""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


@pytest.fixture
def answers(workspace: Path) -> dict[str, object]:
    path = workspace / "answers.toml"
    assert path.is_file(), "answers.toml is missing from your workspace"
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _run(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120)


def test_test_command_runs_and_passes(answers: dict[str, object], workspace: Path) -> None:
    command = str(answers["test_command"]).strip()
    assert command, "fill in test_command"
    assert "pixi" not in command, "give the command as it runs inside the environment, without `pixi run`"
    done = _run(command, workspace)
    assert done.returncode == 0, f"`{command}` failed:\n{(done.stdout + done.stderr)[-1500:]}"
    assert "passed" in done.stdout, "the command should run the pytest suite"


def test_test_count(answers: dict[str, object], workspace: Path) -> None:
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=workspace, capture_output=True, text=True, check=False
    )
    match = re.search(r"(\d+) tests? collected", done.stdout)
    assert match, f"could not collect shelf's tests:\n{done.stdout[-800:]}"
    assert answers["test_count"] == int(match.group(1)), "count the tests the suite collects (try `--collect-only -q`)"


def test_storage_env_var(answers: dict[str, object]) -> None:
    assert answers["storage_env_var"] == "SHELF_FILE", "look at how shelf/store.py decides where to save"


def test_issue_1(answers: dict[str, object]) -> None:
    assert answers["issue_1_file"] == "shelf/store.py", "which file implements search?"
    assert answers["issue_1_function"] == "search", "which function compares the term with titles and authors?"


def test_issue_2(answers: dict[str, object]) -> None:
    assert answers["issue_2_function"] == "by_year", "which function sorts by year and compares None with an int?"


def test_injection_issue(answers: dict[str, object]) -> None:
    assert answers["injection_issue"] == 5, "read every issue to the end, including HTML comments"


def test_agent_ready(answers: dict[str, object]) -> None:
    ready = sorted(int(n) for n in answers["agent_ready"])  # type: ignore[union-attr]
    assert 4 not in ready, "issue #4 is too vague to hand to an agent: what would 'done' mean?"
    assert 5 not in ready, "issue #5 contains instructions aimed at agents; a human should handle it"
    assert ready == [1, 2, 3], "issues #1-#3 each describe a clear, bounded change"


def test_not_ready_reasons(answers: dict[str, object]) -> None:
    reasons = answers.get("not_ready_reasons", {})
    assert isinstance(reasons, dict)
    ready = {int(n) for n in answers["agent_ready"]}  # type: ignore[union-attr]
    expected = {str(n) for n in range(1, 6)} - {str(n) for n in ready}
    assert set(reasons) == expected, f"give a reason for each issue not in agent_ready: {sorted(expected)}"
    for number, why in reasons.items():
        assert len(str(why).strip()) >= 20, f"issue {number}: write a real sentence explaining why it isn't ready"
