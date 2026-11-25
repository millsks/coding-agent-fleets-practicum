# m00-lab1 · Meet shelf

Before you write agents for a codebase, you need to know it well enough to judge their work. Your workspace is a
copy of `shelf`, the small book-tracking CLI every lab uses. Read it, run it, and answer the questions in
`answers.toml`. Every answer is checked against the code, so guessing won't pass.

```sh
pixi run start m00-lab1
cd work/m00-lab1
pixi run python -m shelf --help        # try the tool
pixi run python -m pytest -q           # run its tests
# edit answers.toml
cd ../..
pixi run grade m00-lab1
```

## What to fill in

| Key | Question |
| --- | --- |
| `test_command` | The command that runs shelf's tests from the workspace root (without `pixi run`). It must pass. |
| `test_count` | How many tests the suite collects. |
| `storage_env_var` | The environment variable that changes where the shelf is stored. |
| `issue_1_file` | The file (path relative to the workspace) that contains the bug behind issue #1. |
| `issue_1_function` | The function in that file that has the bug. |
| `issue_2_function` | The function that raises the error in issue #2. |
| `injection_issue` | The number of the issue that tries to give AI agents instructions. |
| `agent_ready` | The issue numbers that are clear and bounded enough to hand to an agent today, as a list. |
| `not_ready_reasons` | For every issue *not* in `agent_ready`, a sentence on why, keyed by its number as a string. |

## Done when

`pixi run grade m00-lab1` passes. Then keep your answers: you'll check your triager agent against them later.
