# m02-lab1 · A reviewer and a test writer

Write the first two agents of your fleet for the shelf project:

- `.claude/agents/reviewer.md`: reviews a change and decides whether it can merge.
- `.claude/agents/test-writer.md`: turns a spec or bug report into tests, starting with a failing one.

```sh
pixi run start m02-lab1
# edit work/m02-lab1/.claude/agents/reviewer.md and test-writer.md
pixi run grade m02-lab1
pixi run grade-live m02-lab1   # optional: run your reviewer on the seeded bad fix with the real claude CLI
```

## Specification: reviewer

| Requirement | Why |
| --- | --- |
| Valid frontmatter (`fleetlab.check_agent` reports no problems), `name: reviewer` | Typos are silently ignored at runtime |
| `tools` set explicitly, including `Read`, `Grep`, and `Glob`; no `Edit`, `Write`, `MultiEdit`, or `NotebookEdit` after `disallowedTools`; no `Agent` | Least privilege: a reviewer reads and never edits or delegates |
| `model` set; `maxTurns` between 5 and 40 | Deliberate cost and a hard budget |
| `description` under 250 characters that says when to use it (contains "Use") | Delegation happens at the right moment |
| The prompt states a boundary (it never edits files) | Role and boundary |
| The prompt defines the output: findings labelled `BLOCKING` or `NIT`, each with `file:line`, ending with exactly one line, either `VERDICT: approve` or `VERDICT: changes requested` | A script will read the verdict in Stage 2 |
| The prompt says when to stop or hand back (for example, no diff, or a decision only a human can make) | Stop conditions |

## Specification: test-writer

| Requirement | Why |
| --- | --- |
| Valid frontmatter, `name: test-writer` | |
| `tools` set explicitly, including `Read` and at least one of `Write` or `Edit`; no `Agent` | It writes test files and doesn't delegate |
| `model` set; `maxTurns` between 5 and 40; a `description` under 250 characters that contains "Use" | |
| The prompt keeps it to `tests/` and says it never changes code outside it | M04 will enforce this with a hook; the prompt sets the expectation |
| The prompt works from the spec's or issue's acceptance criteria, and for a bug writes a test that fails before the fix | Tests check intent, not the implementation |
| The prompt says when to stop or hand back | Stop conditions |

## Live check (optional)

`pixi run grade-live m02-lab1` applies `labs/m02-lab1/seeded/bad-fix.patch` (a wrong fix for issue #1) in a copy of
your workspace and asks Claude to use your reviewer on it. It passes if the review ends with
`VERDICT: changes requested`. Run it a few times: a reviewer that only sometimes catches the problem needs a better
prompt. See `labs/m02-lab1/seeded/README.md` to run the same review by hand.

## Done when

`pixi run grade m02-lab1` passes, and you've run the reviewer on the seeded change at least three times.
