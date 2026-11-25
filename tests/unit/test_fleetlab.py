import json
import sys
from pathlib import Path

import pytest

import fleetlab
from fleetlab import frontmatter, hooks, settings, transcript
from fleetlab.agents import check_agent, load_agent
from fleetlab.skills import check_skill

AGENT = """---
name: reviewer
description: Reviews diffs. Use after code changes.
tools: Read, Grep, Glob
model: sonnet
maxTurns: 20
---

You review code.
"""


# --- frontmatter -----------------------------------------------------------------------------------------------


def test_parse_scalars_lists_and_body() -> None:
    doc = frontmatter.parse(
        "---\nname: x\n# c\ntools: Read, Grep\nskills: [a, 'b']\nn: 3\nneg: -1\nflag: true\nq: 'quoted: yes'\n---\n\nBody\n"
    )
    assert doc.meta == {
        "name": "x",
        "tools": ["Read", "Grep"],
        "skills": ["a", "b"],
        "n": 3,
        "neg": -1,
        "flag": True,
        "q": "quoted: yes",
    }
    assert doc.body == "Body"


def test_parse_block_list_and_nested_mapping() -> None:
    doc = frontmatter.parse("---\ntools:\n  - Read\n  - Grep\nhooks:\n  Stop:\n    - x\n---\nb")
    assert doc.meta["tools"] == ["Read", "Grep"]
    assert "Stop:" in str(doc.meta["hooks"])


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("name: x\n", "must start"),
        ("---\nname: x\n", "no closing"),
        ("---\n  indented: x\n---\n", "no key above"),
        ("---\nnot a pair\n---\n", "expected 'key: value'"),
        ("---\na: 1\na: 2\n---\n", "appears twice"),
    ],
)
def test_parse_errors(text: str, message: str) -> None:
    with pytest.raises(frontmatter.FrontmatterError, match=message):
        frontmatter.parse(text)


# --- agents ----------------------------------------------------------------------------------------------------


def test_valid_agent_has_no_problems() -> None:
    spec = check_agent(AGENT, "reviewer.md")
    assert spec.problems == []
    assert spec.name == "reviewer"
    assert spec.tools == {"Read", "Grep", "Glob"}
    assert not spec.can_write()


def test_agent_problems_are_reported() -> None:
    text = (
        "---\nname: rev\ntools: Read, Hammer\nmodel: gpt\npermissionMode: yolo\nisolation: vm\n"
        "effort: huge\nmaxTurns: 0\nmaxturns: 5\n---\n"
    )
    problems = " | ".join(check_agent(text, "reviewer.md").problems)
    for fragment in (
        "missing required field 'description'",
        "does not match the file name",
        "unknown field 'maxturns'",
        "unknown tool 'Hammer'",
        "unknown model 'gpt'",
        "unknown permissionMode",
        "isolation must be",
        "unknown effort",
        "maxTurns must be",
        "body is empty",
    ):
        assert fragment in problems


def test_agent_bad_name_and_tools_shape() -> None:
    spec = check_agent("---\nname: a:b\ndescription: d\ntools: 3\n---\nbody")
    assert any("contain no ':'" in p for p in spec.problems)
    assert any("unknown tool '3'" in p for p in spec.problems)


def test_agent_frontmatter_error_is_a_problem() -> None:
    assert check_agent("no frontmatter").problems == ["the file must start with a line containing only '---'"]


def test_can_write_rules() -> None:
    assert check_agent("---\nname: a\ndescription: d\n---\nb").can_write()
    inherit_blocked = check_agent(
        "---\nname: a\ndescription: d\ndisallowedTools: Edit, Write, MultiEdit, NotebookEdit, Bash\n---\nb"
    )
    assert not inherit_blocked.can_write()
    listed = check_agent("---\nname: a\ndescription: d\ntools: Read, Bash\ndisallowedTools: Bash\n---\nb")
    assert listed.tools == {"Read"}
    assert not listed.can_write()
    assert check_agent("---\nname: a\ndescription: d\ntools: Read, Edit\n---\nb").can_write()


def test_mcp_and_scoped_tools_are_allowed() -> None:
    spec = check_agent("---\nname: a\ndescription: d\ntools: mcp__github__get_issue, Bash(git *)\n---\nb")
    assert spec.problems == []


def test_load_agent(tmp_path: Path) -> None:
    path = tmp_path / "reviewer.md"
    path.write_text(AGENT, encoding="utf-8")
    assert load_agent(path).problems == []


# --- skills ----------------------------------------------------------------------------------------------------


def test_valid_skill() -> None:
    assert check_skill("---\nname: add-command\ndescription: Add a CLI command.\n---\nSteps", "add-command") == []


@pytest.mark.parametrize(
    ("text", "folder", "fragment"),
    [
        ("---\ndescription: d\n---\nb", "x", "missing required field 'name'"),
        ("---\nname: Bad_Name\ndescription: d\n---\nb", "Bad_Name", "lowercase"),
        ("---\nname: a\ndescription: d\n---\nb", "b", "must match its folder"),
        ("---\nname: a\n---\nb", "a", "missing required field 'description'"),
        ("---\nname: a\ndescription: " + "x" * 1100 + "\n---\nb", "a", "the limit is 1024"),
        ("---\nname: a\ndescription: d\ntools: Read\n---\nb", "a", "not part of the Agent Skills format"),
        ("---\nname: a\ndescription: d\n---\n", "a", "body is empty"),
        ("---\nname: a\ndescription: d\n---\n" + "line\n" * 600, "a", "over 500 lines"),
        ("nothing", "a", "must start"),
    ],
)
def test_skill_problems(text: str, folder: str, fragment: str) -> None:
    assert any(fragment in p for p in check_skill(text, folder))


# --- hooks -----------------------------------------------------------------------------------------------------


def _guard() -> None:
    data = json.load(sys.stdin)
    if "--force" in data["tool_input"].get("command", ""):
        print("force pushes are not allowed", file=sys.stderr)
        sys.exit(2)


def test_payload_builders() -> None:
    payload = hooks.pre_tool_use("Bash", {"command": "ls"})
    assert payload["hook_event_name"] == "PreToolUse"
    assert payload["tool_input"] == {"command": "ls"}
    assert {"session_id", "transcript_path", "cwd", "permission_mode", "tool_use_id"} <= set(payload)
    stop = hooks.stop(active=True, last_message="done")
    assert stop["stop_hook_active"] is True
    assert stop["last_assistant_message"] == "done"


def test_run_hook_block_and_allow() -> None:
    blocked = hooks.run_hook(_guard, hooks.pre_tool_use("Bash", {"command": "git push --force"}))
    assert (blocked.exit_code, blocked.blocked, blocked.decision) == (2, True, "block")
    assert blocked.reason == "force pushes are not allowed"
    allowed = hooks.run_hook(_guard, hooks.pre_tool_use("Bash", {"command": "git status"}))
    assert (allowed.exit_code, allowed.blocked, allowed.decision, allowed.reason) == (0, False, None, "")


def test_run_hook_exit_variants() -> None:
    def exits(code: object) -> object:
        def main() -> None:
            raise SystemExit(code)

        return main

    assert hooks.run_hook(exits(None), {}).exit_code == 0
    text_exit = hooks.run_hook(exits("bad"), {})
    assert (text_exit.exit_code, text_exit.stderr.strip()) == (1, "bad")

    def crash() -> None:
        raise ValueError("oops")

    crashed = hooks.run_hook(crash, {})
    assert crashed.exit_code == 1
    assert "ValueError: oops" in crashed.stderr
    assert not crashed.blocked


def test_json_decisions() -> None:
    deny = hooks.HookResult(
        0,
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "no",
                }
            }
        ),
    )
    assert (deny.decision, deny.blocked, deny.reason) == ("deny", True, "no")
    block = hooks.HookResult(0, json.dumps({"decision": "block", "reason": "tests red"}))
    assert (block.decision, block.blocked, block.reason) == ("block", True, "tests red")
    assert hooks.HookResult(0, "{}").decision is None
    assert hooks.HookResult(0, "not json").json is None
    assert hooks.HookResult(0, "{broken").json is None
    assert hooks.HookResult(0, "[1]").json is None
    assert hooks.HookResult(1, json.dumps({"decision": "block"})).decision is None


def test_run_script_python_shell_and_timeout(tmp_path: Path) -> None:
    py = tmp_path / "hook.py"
    py.write_text("import json, sys\nd = json.load(sys.stdin)\nprint(d['tool_name'], file=sys.stderr)\nsys.exit(2)\n")
    result = hooks.run_script(py, hooks.pre_tool_use("Bash", {"command": "x"}))
    assert (result.exit_code, result.stderr.strip()) == (2, "Bash")
    sh = tmp_path / "hook.sh"
    sh.write_text("cat > /dev/null\necho ok\n")
    assert hooks.run_script(sh, {}).stdout.strip() == "ok"
    exe = tmp_path / "hook"
    exe.write_text("#!/bin/sh\nexit 3\n")
    exe.chmod(0o755)
    assert hooks.run_script(exe, {}).exit_code == 3
    slow = tmp_path / "slow.py"
    slow.write_text("import time\ntime.sleep(5)\n")
    assert hooks.run_script(slow, {}, timeout=0.5).exit_code == 124


# --- settings --------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("matcher", "tool", "expected"),
    [
        (None, "Bash", True),
        ("", "Bash", True),
        ("*", "Bash", True),
        ("Bash", "Bash", True),
        ("Bash", "BashX", False),
        ("Edit|Write", "Write", True),
        ("Edit, Write", "Edit", True),
        ("^Notebook", "NotebookEdit", True),
        ("mcp__memory__.*", "mcp__memory__save", True),
        ("mcp__memory__.*", "mcp__other__save", False),
    ],
)
def test_matcher_rules(matcher: str | None, tool: str, expected: bool) -> None:
    assert settings.matcher_matches(matcher, tool) is expected


def test_hook_commands() -> None:
    config = {
        "hooks": {
            "PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": "guard.py"}]},
                {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "paths.py"}]},
                "junk",
                {"hooks": [{"type": "prompt", "prompt": "x"}, {"command": "all.py"}, "junk"]},
            ],
            "Stop": [{"hooks": [{"type": "command", "command": "green.py"}]}],
        }
    }
    assert settings.hook_commands(config, "PreToolUse", "Bash") == ["guard.py", "all.py"]
    assert settings.hook_commands(config, "PreToolUse", "Write") == ["paths.py", "all.py"]
    assert settings.hook_commands(config, "Stop") == ["green.py"]
    assert settings.hook_commands({}, "Stop") == []
    assert settings.hook_commands({"hooks": {"Stop": "bad"}}, "Stop") == []


# --- transcript ------------------------------------------------------------------------------------------------

STREAM = "\n".join(
    json.dumps(line)
    for line in [
        {
            "type": "system",
            "subtype": "init",
            "session_id": "s1",
            "model": "claude-sonnet-5-5",
            "tools": ["Read", "Bash"],
        },
        {
            "type": "assistant",
            "parent_tool_use_id": None,
            "message": {
                "content": [
                    {"type": "text", "text": "Looking."},
                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "pytest -q"}},
                ]
            },
        },
        {
            "type": "user",
            "parent_tool_use_id": None,
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "t1",
                        "content": [{"type": "text", "text": "1 failed"}],
                        "is_error": True,
                    },
                ]
            },
        },
        {
            "type": "assistant",
            "parent_tool_use_id": "t9",
            "message": {
                "content": [
                    {"type": "text", "text": "sub text"},
                    {"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": "a.py"}},
                    "junk",
                ]
            },
        },
        {
            "type": "user",
            "parent_tool_use_id": "t9",
            "message": {
                "content": [
                    {"type": "tool_result", "tool_use_id": "t2", "content": "print(1)"},
                    {"type": "tool_result", "tool_use_id": "unknown", "content": "x"},
                ]
            },
        },
        {"type": "assistant", "parent_tool_use_id": None, "message": {"content": "not a list"}},
        {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "num_turns": 4,
            "total_cost_usd": 0.0123,
            "result": "Fixed.",
        },
    ]
)


def test_parse_stream() -> None:
    run = transcript.parse_stream(STREAM + "\nnot json\n{broken\n\n")
    assert (run.session_id, run.model, run.tools) == ("s1", "claude-sonnet-5-5", ["Read", "Bash"])
    assert [c.name for c in run.calls] == ["Bash", "Read"]
    assert run.calls[0].result == "1 failed" and run.calls[0].is_error
    assert run.calls[1].parent == "t9" and run.calls[1].result == "print(1)"
    assert run.texts == ["Looking."]
    assert run.finished and run.succeeded
    assert (run.num_turns, run.cost_usd) == (4, 0.0123)
    assert run.calls_by_tool() == {"Bash": 1, "Read": 1}


def test_unfinished_stream() -> None:
    run = transcript.parse_stream(STREAM.splitlines()[0])
    assert not run.finished and not run.succeeded
    assert (run.num_turns, run.cost_usd) == (0, 0.0)


# --- context and package ---------------------------------------------------------------------------------------


def test_estimate_tokens() -> None:
    assert fleetlab.estimate_tokens("") == 0
    assert fleetlab.estimate_tokens("ab") == 1
    assert fleetlab.estimate_tokens("x" * 400) == 100


def test_public_api() -> None:
    for name in fleetlab.__all__:
        assert hasattr(fleetlab, name)
