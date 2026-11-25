# m03-lab1 · Instructions and a first skill

Write the instructions every agent in your fleet reads when it works on shelf, and the first procedure it can load
on demand.

```sh
pixi run start m03-lab1
# edit work/m03-lab1/AGENTS.md and CLAUDE.md; create work/m03-lab1/.claude/skills/add-command/
pixi run grade m03-lab1
```

## Specification: AGENTS.md

- At most 150 lines and well under 16 KiB (the check allows 8 KiB: leave headroom).
- A one-paragraph description of the project before the first section.
- `## Commands`: bullet lines with each command in single backticks. At least two commands, at least one of which runs
  the test suite with `pytest`. **The checks run every command** in a fresh copy of your workspace (without
  `pixi run`, as agents will inside the environment), so each must succeed. Don't list commands that change state,
  like `git push`, or that need input.
- `## Map`: where things live. Mention `shelf/`, `tests/`, and `issues/`, and say what each holds.
- `## Rules`: at least three bullet rules. One must be about tests (for example, never deleting, skipping, or loosening
  them).
- No secrets: nothing that looks like an API key.

## Specification: CLAUDE.md

- The first non-empty line is exactly `@AGENTS.md`, so Claude Code reads the shared instructions. Anything after it
  is for Claude Code only.

## Specification: the add-command skill

Create `.claude/skills/add-command/SKILL.md`: the procedure for adding a new subcommand to shelf's CLI (for example
`python -m shelf count`).

- Valid in the Agent Skills format (`fleetlab.check_skill` reports no problems): `name: add-command`, a description
  under 1,024 characters that says when to use it (contains "Use").
- The body names the files involved: `shelf/cli.py` and `tests/test_cli.py`.
- The body links to a `reference.md` in the same folder, and that file exists and isn't empty. Put the detail an
  agent only sometimes needs there (for example, how `build_parser` and `main` fit together, and an example test).

## Try it

Ask an agent to use the skill, and read the transcript with your m01 summariser:

```sh
cd work/m03-lab1
claude -p "Add a 'count' subcommand that prints how many books are on the shelf." \
  --allowedTools "Read,Grep,Glob,Edit,Write,Bash(python -m pytest *)" --max-turns 30 \
  --output-format stream-json --verbose > ../count-run.jsonl
```

## Done when

`pixi run grade m03-lab1` passes.
