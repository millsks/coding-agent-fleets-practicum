"""Build hook payloads and run hook code against them.

Claude Code runs a command hook by starting your command, writing one JSON object to its stdin, and reading three
things back: the exit code, stdout, and stderr.

* Exit 0: the action goes ahead. If stdout is exactly one JSON object, Claude Code reads it for a decision.
* Exit 2: a blocking error. On events that can block (``PreToolUse``, ``Stop``, ...) the action is stopped and
  stderr is shown to Claude as the reason.
* Any other exit code: a non-blocking error. The action goes ahead and the transcript notes that the hook failed.
  Exit 1 does **not** block.

:func:`run_hook` runs a Python ``main()`` function in-process (this is what lesson exercises use in the browser).
:func:`run_script` runs a real hook file in a subprocess (this is what lab checks use).
"""

import contextlib
import io
import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BLOCKING_EXIT_CODE = 2


def _common(event: str, cwd: str, permission_mode: str, session_id: str) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "transcript_path": f"/home/dev/.claude/projects/demo/{session_id}.jsonl",
        "cwd": cwd,
        "permission_mode": permission_mode,
        "hook_event_name": event,
    }


def pre_tool_use(
    tool_name: str,
    tool_input: dict[str, Any] | None = None,
    *,
    cwd: str = "/home/dev/shelf",
    permission_mode: str = "default",
    session_id: str = "sess-0001",
) -> dict[str, Any]:
    """Build the payload Claude Code sends to a ``PreToolUse`` hook.

    Args:
        tool_name: Tool about to run, such as ``Bash`` or ``Edit``.
        tool_input: The tool's arguments, such as ``{"command": "git status"}``.
        cwd: Working directory of the session.
        permission_mode: The session's permission mode.
        session_id: Session identifier.

    Returns:
        The payload as a dictionary (serialise it with ``json.dumps`` to feed a script).
    """
    payload = _common("PreToolUse", cwd, permission_mode, session_id)
    payload.update({"tool_name": tool_name, "tool_input": dict(tool_input or {}), "tool_use_id": "toolu_01demo"})
    return payload


def stop(
    *, active: bool = False, last_message: str = "Done.", cwd: str = "/home/dev/shelf", session_id: str = "sess-0001"
) -> dict[str, Any]:
    """Build the payload Claude Code sends to a ``Stop`` hook when the agent tries to finish.

    Args:
        active: ``stop_hook_active``: true when Claude is already continuing because a Stop hook blocked it.
        last_message: The agent's final message.
        cwd: Working directory of the session.
        session_id: Session identifier.

    Returns:
        The payload as a dictionary.
    """
    payload = _common("Stop", cwd, "default", session_id)
    payload.update({"stop_hook_active": active, "last_assistant_message": last_message})
    return payload


@dataclass(frozen=True)
class HookResult:
    """What a hook returned.

    Attributes:
        exit_code: Process exit code.
        stdout: Everything printed to stdout.
        stderr: Everything printed to stderr.
    """

    exit_code: int
    stdout: str = ""
    stderr: str = ""

    @property
    def json(self) -> dict[str, Any] | None:
        """Stdout parsed as one JSON object, or ``None`` when it is not exactly one object."""
        text = self.stdout.strip()
        if not text.startswith("{"):
            return None
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None

    @property
    def decision(self) -> str | None:
        """The decision Claude Code would act on: ``block`` or ``deny`` to stop, ``allow`` or ``ask``, else ``None``."""
        if self.exit_code == BLOCKING_EXIT_CODE:
            return "block"
        data = self.json if self.exit_code == 0 else None
        if not data:
            return None
        specific = data.get("hookSpecificOutput")
        if isinstance(specific, dict) and specific.get("permissionDecision"):
            return str(specific["permissionDecision"])
        if data.get("decision") == "block":
            return "block"
        return None

    @property
    def blocked(self) -> bool:
        """Whether the action would be stopped."""
        return self.decision in ("block", "deny")

    @property
    def reason(self) -> str:
        """The text Claude would see as the reason, from stderr (exit 2) or the JSON output."""
        if self.exit_code == BLOCKING_EXIT_CODE:
            return self.stderr.strip()
        data = self.json or {}
        specific = data.get("hookSpecificOutput")
        if isinstance(specific, dict) and specific.get("permissionDecisionReason"):
            return str(specific["permissionDecisionReason"])
        return str(data.get("reason", ""))


def run_hook(main: Callable[[], object], payload: dict[str, Any]) -> HookResult:
    """Run a hook's ``main()`` in this process with ``payload`` on stdin.

    ``main`` reads ``sys.stdin``, prints, and calls ``sys.exit(code)`` exactly as a real hook script does, so the same
    function works when the file runs under Claude Code.

    Args:
        main: The hook's entry point.
        payload: The event payload, for example from :func:`pre_tool_use`.

    Returns:
        The captured result.
    """
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    code = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                main()
            except SystemExit as exc:
                if exc.code is None:
                    code = 0
                elif isinstance(exc.code, int):
                    code = exc.code
                else:
                    print(exc.code, file=sys.stderr)
                    code = 1
            except Exception as exc:  # a crashing hook is a non-blocking error, like a real one
                print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
                code = 1
    finally:
        sys.stdin = old_stdin
    return HookResult(code, out.getvalue(), err.getvalue())


def run_script(
    path: Path | str,
    payload: dict[str, Any],
    *,
    cwd: Path | str | None = None,
    env: dict[str, str] | None = None,
    timeout: float = 60,
) -> HookResult:
    """Run a hook file as a subprocess, the way Claude Code does.

    ``.py`` files run with this Python interpreter and ``.sh`` files with ``bash``; anything else runs directly.

    Args:
        path: The hook script.
        payload: The event payload.
        cwd: Working directory for the process.
        env: Environment for the process (defaults to this process's environment).
        timeout: Seconds before the hook is treated as hung.

    Returns:
        The captured result. A hung hook returns exit code 124.
    """
    script = Path(path)
    if script.suffix == ".py":
        command = [sys.executable, str(script)]
    elif script.suffix == ".sh":
        command = ["bash", str(script)]
    else:
        command = [str(script)]
    try:
        done = subprocess.run(
            command,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return HookResult(124, "", f"hook timed out after {timeout:.0f}s")
    return HookResult(done.returncode, done.stdout, done.stderr)
