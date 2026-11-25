# m04-lab2 · Checks must pass before stopping

Write `.claude/hooks/require_green.py`, a `Stop` hook that refuses to let an agent finish while shelf's checks fail,
and wire it into `.claude/settings.json`.

```sh
pixi run start m04-lab2
# edit work/m04-lab2/.claude/hooks/require_green.py, .claude/check-command, and .claude/settings.json
pixi run grade m04-lab2
```

## Specification

1. Read the payload from stdin. If `stop_hook_active` is true, exit 0 immediately **without running anything**.
2. Find the project directory: `$CLAUDE_PROJECT_DIR` if set, otherwise the payload's `cwd`, otherwise the current
   directory.
3. Read the check command: the first line of `<project>/.claude/check-command` that isn't blank and doesn't start with
   `#`. If the file is missing or has no command, print a short note to stderr and exit 0.
4. Run the command through the shell in the project directory, capturing stdout and stderr together, with a timeout of
   `$CHECK_TIMEOUT` seconds (default 300).
5. If it exits 0, exit 0.
6. If it fails, print a first line starting with `Checks failed` to stderr, followed by the **last 40 lines** of its
   output, and exit 2.
7. If it times out, print a message containing `timed out` to stderr and exit 2.

Also:

- `.claude/check-command` runs shelf's fast checks (its pytest suite) and passes on the untouched project.
- `.claude/settings.json` runs the hook on `Stop`, with `$CLAUDE_PROJECT_DIR` in the command.

## Try it live

In `work/m04-lab2/`, ask Claude Code to fix issue #2 (`list --by-year` crashes on books without a year) *and* add a
test for it. If its first attempt breaks a test, watch the gate send it back with the failure. Then try the same task
with the hook removed from settings and compare the transcripts.

## Done when

`pixi run grade m04-lab2` passes.
