# m01-lab1 · A run summariser

Write `summarize_run.py`: a command-line tool that reads the transcript of a headless run
(`claude -p ... --output-format stream-json --verbose`) and prints a one-object JSON summary. You'll use it on every
agent you run in this course.

```sh
pixi run start m01-lab1
# write work/m01-lab1/summarize_run.py
pixi run grade m01-lab1
pixi run grade-live m01-lab1   # optional: summarise a real run of claude on shelf
```

## Specification

`python summarize_run.py TRANSCRIPT` prints exactly one JSON object to stdout and exits 0. If the file doesn't exist,
print a message to stderr and exit 2.

| Key | Value |
| --- | --- |
| `finished` | `true` if the transcript has a `{"type": "result", ...}` event |
| `succeeded` | `true` if that event has `subtype` `"success"` and `is_error` false; `false` otherwise (including unfinished runs) |
| `turns` | the result's `num_turns`, or `0` if unfinished |
| `cost_usd` | the result's `total_cost_usd` as a number, or `0` if unfinished |
| `tool_calls` | `{tool name: count}` for calls in the **main conversation** (`parent_tool_use_id` is `null`) |
| `subagent_tool_calls` | the same, for calls made inside subagents (`parent_tool_use_id` is set) |
| `failed_calls` | every call whose `tool_result` has `is_error: true`, in order, as `{"tool": name, "input": {...}}` |
| `warnings` | a list containing any of the strings below, in this order |

Warnings:

- `"unfinished"`: there is no result event.
- `"unverified_edits"`: there is at least one `Edit` or `Write` call, and no `Bash` call whose command contains
  `pytest` comes after the last one.
- `"doom_loop"`: three or more consecutive calls (in transcript order, main and subagent together) with the same tool
  name and the same input, all of which failed.

Rules:

- Skip lines that are blank or aren't JSON objects. Real transcripts can contain stray log lines.
- Use only the Python standard library. Do **not** import `fleetlab`: in a work sandbox you may have nothing but Python.

## Done when

`pixi run grade m01-lab1` passes. The checks run your script against four recorded transcripts in
`labs/m01-lab1/tests/fixtures/`: a clean run, a premature "done", a doom loop with a subagent, and a run cut off
before its result line. Read them: they are realistic examples of what you'll see from real agents.
