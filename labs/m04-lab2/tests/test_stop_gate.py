"""Checks for m04-lab2: the Stop gate runs in copies of shelf with passing, failing, and hanging checks."""

import json
import os
import shutil
import sys
import time
from pathlib import Path

import pytest

import fleetlab

PY = sys.executable


@pytest.fixture
def hook(workspace: Path) -> Path:
    path = workspace / ".claude" / "hooks" / "require_green.py"
    assert path.is_file(), ".claude/hooks/require_green.py is missing"
    return path


@pytest.fixture
def project(workspace: Path, tmp_path: Path) -> Path:
    copy = tmp_path / "project"
    shutil.copytree(workspace, copy)
    return copy


def set_command(project: Path, command: str) -> None:
    (project / ".claude" / "check-command").write_text(f"# check command\n\n{command}\n", encoding="utf-8")


def stop(
    hook: Path, project: Path, *, active: bool = False, env: dict[str, str] | None = None, cwd: Path | None = None
) -> fleetlab.HookResult:
    full_env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project), **(env or {})}
    return fleetlab.run_script(
        hook, fleetlab.stop(active=active, cwd=str(project)), cwd=cwd or project, env=full_env, timeout=120
    )


def test_check_command_runs_shelf_tests(workspace: Path, hook: Path) -> None:
    path = workspace / ".claude" / "check-command"
    lines = [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert lines, "put the check command in .claude/check-command"
    assert "pytest" in lines[0], "the check command should run shelf's pytest suite"
    result = stop(hook, workspace)
    assert result.exit_code == 0, (
        f"on the untouched project the checks pass, so the agent may stop:\n{result.stderr[-800:]}"
    )


def test_failing_shelf_test_blocks(hook: Path, project: Path) -> None:
    (project / "tests" / "test_gate_failure.py").write_text(
        "def test_gate_failure():\n    assert 1 == 2\n", encoding="utf-8"
    )
    result = stop(hook, project)
    assert result.exit_code == 2, f"a failing test must block with exit 2 (got {result.exit_code})"
    assert result.stderr.startswith("Checks failed"), "start stderr with 'Checks failed'"
    assert "test_gate_failure" in result.stderr, "include the end of the test output so the agent sees what failed"


def test_sends_only_the_tail(hook: Path, project: Path) -> None:
    set_command(project, f"{PY} -c \"import sys; [print(f'line {{i}}') for i in range(1, 201)]; sys.exit(1)\"")
    result = stop(hook, project)
    assert result.exit_code == 2
    assert "line 200" in result.stderr and "line 161" in result.stderr, "include the last 40 lines"
    assert "line 150" not in result.stderr, "send only the last 40 lines, not the whole output"


def test_captures_stderr_output(hook: Path, project: Path) -> None:
    set_command(project, f"{PY} -c \"import sys; print('boom on stderr', file=sys.stderr); sys.exit(3)\"")
    result = stop(hook, project)
    assert result.exit_code == 2 and "boom on stderr" in result.stderr, "capture the command's stderr too"


def test_stop_hook_active_lets_go_without_running(hook: Path, project: Path) -> None:
    marker = project / "ran.txt"
    set_command(project, f"{PY} -c \"open('ran.txt', 'w').write('x'); raise SystemExit(1)\"")
    result = stop(hook, project, active=True)
    assert result.exit_code == 0, "when stop_hook_active is true, let the agent stop"
    assert not marker.exists(), "don't run the checks again when stop_hook_active is true"


def test_missing_check_command_allows(hook: Path, project: Path) -> None:
    (project / ".claude" / "check-command").unlink()
    result = stop(hook, project)
    assert result.exit_code == 0, "with no check command configured, let the agent stop"


def test_timeout(hook: Path, project: Path) -> None:
    set_command(project, f'{PY} -c "import time; time.sleep(30)"')
    started = time.monotonic()
    result = stop(hook, project, env={"CHECK_TIMEOUT": "1"})
    assert time.monotonic() - started < 15, "honour CHECK_TIMEOUT"
    assert result.exit_code == 2 and "timed out" in result.stderr, "a hanging check must block with 'timed out'"


def test_uses_project_dir_not_cwd(hook: Path, project: Path, tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    set_command(project, f'{PY} -c "raise SystemExit(1)"')
    result = stop(hook, project, cwd=elsewhere)
    assert result.exit_code == 2, "find the project through $CLAUDE_PROJECT_DIR, not the current directory"


def test_settings_wiring(workspace: Path) -> None:
    settings = json.loads((workspace / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = fleetlab.hook_commands(settings, "Stop")
    assert any("require_green.py" in c for c in commands), "run require_green.py on Stop"
    assert all("$CLAUDE_PROJECT_DIR" in c for c in commands if "require_green.py" in c), (
        "use $CLAUDE_PROJECT_DIR in the command"
    )
