# Authoring Guide

How lesson, project, and reference pages in `docs/` are built. The live gallery of every component is
`docs/authoring/components.html` (`pixi run serve`, then open `/authoring/components.html`).

`pixi run check-site` validates links, anchors, quizzes, exercise test blocks, and visualizer names. It must pass.

## Page skeleton

Module pages live at `docs/modules/<id>-<slug>.html` with the exact `href` from `docs/assets/js/curriculum.js`.
Project pages live at `docs/projects/`, reference pages at `docs/reference/`. All use `data-root="../"`.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>M02 · Writing a Subagent · Coding Agent Fleets Practicum</title>
<link rel="stylesheet" href="../assets/css/course.css">
<script src="../assets/js/curriculum.js"></script>
<script src="../assets/js/fleetlab-src.js"></script>
<script src="../assets/js/viz.js" defer></script>
<script src="../assets/js/viz-agent.js" defer></script>
<script src="../assets/js/course.js" defer></script>
</head>
<body data-root="../" data-module="m09">
<main class="lesson">
  <header class="lesson-hero">
    <p class="eyebrow">Stage 2 · Tool Use and the Agent Loop · Module 09</p>
    <h1>Functions</h1>
    <p class="lede">One or two sentences on why this matters.</p>
    <div class="lesson-meta"><span>⏱ ~2.5 hours</span><span>Prerequisites: <a href="m04-control-flow.html">M04</a></span></div>
    <ul class="objectives"><li>…</li></ul>
  </header>
  <section class="lesson-section" id="some-topic"><h2>Some topic</h2> … </section>
  …
</main>
</body>
</html>
```

`course.js` wraps `<main>` with the header, sidebar, table of contents (built from each
`section.lesson-section[id] > h2`), the "Mark complete" box, notes, and previous/next links. Do not write those yourself.
Capstone pages use `data-module="c1"` (the manifest id) so completion tracking works; reference pages use
`data-page="ref-glossary"` etc.

## Required module structure

1. Hero: eyebrow, `h1`, lede, meta (time and prerequisites), objectives (4–7 items).
2. Six to ten teaching sections. Each one explains the idea in plain language, shows a worked example, and makes the
   learner do something: a runnable cell, a `data-predict` cell, a tracer, a visualizer, a transcript to diagnose, or a "think" callout.
3. `id="practice"`: three to six graded exercises, from easy to hard.
4. `id="mini-project"`: a `.project-box` with a small build the learner does locally with Pixi
   (spec, acceptance criteria as a `.checklist`, stretch goals).
5. `id="quiz"`: an end-of-module quiz of 10–15 questions mixing `single`, `multi`, `output`, and `text`.
6. `id="recap"`: a summary list, flashcards (8–12 cards), and "Going further" links to platform.claude.com/docs,
   docs.python.org, and similar.

Write for a motivated beginner who becomes a professional: define every term on first use, explain *why* as well as
*how*, show common mistakes, and finish each section with what to remember. Aim for the depth of a good textbook chapter.

## Components

### Static code

```html
<pre><code class="language-python">x = 1 &lt; 2</code></pre>
<pre data-label="Terminal"><code class="language-bash">pixi run python app.py</code></pre>
```

Escape `<`, `>`, and `&` inside `<pre>`. Languages: python, bash, toml, yaml, json, sql, ini, diff.

### Runnable cells (Pyodide, real CPython in the browser)

```html
<div class="runnable" data-title="Try it">
<textarea>
print("hello")
</textarea>
</div>
```

- Code inside `<textarea>` is written literally (no escaping) and dedented automatically. Never write `</textarea>`.
- `data-predict`: the learner must type a prediction, then Run compares it to the real output.
- `data-stdin="line1\nline2"`: lines fed to `input()`.
- `data-autorun`: run on page load (use sparingly).
- `data-local="reason"`: code that cannot run in the browser (threads needing real parallelism, multiprocessing,
  subprocess, sockets/network, `asyncio.run` with real I/O, packages missing from Pyodide such as torch, polars,
  duckdb, httpx, fastapi, structlog). The reason is shown to the learner.
- Browser packages that load automatically on import: the stdlib and `fleetlab`. The `claude` CLI and the `claude-agent-sdk` package are not
  available in the browser; cells that need it use `data-local`.
- matplotlib figures are rendered automatically after the cell finishes. Do not call `plt.show()`; it's unnecessary.
- `asyncio`: use top-level `await main()` in browser cells and explain that local scripts use `asyncio.run(main())`.

### Step-through tracer

```html
<div class="tracer" data-title="Watch the recursion">
<textarea>
def fact(n):
    return 1 if n == 0 else n * fact(n - 1)
result = fact(4)
</textarea>
</div>
```

Records every line, call, and return; shows frames, locals, changed values, and object-identity tags (two names with
the same "obj N" tag point to the same object). Keep programs small (under 1500 steps). Optional `data-stdin`.

### Exercises (auto-graded in the browser)

```html
<div class="exercise" data-id="m09-e1" data-title="Write is_even">
  <div class="exercise-prompt"><p>Task description…</p></div>
<textarea class="starter">
def is_even(n):
    ...
</textarea>
  <script type="text/x-python" class="tests">
def test_even():
    assert is_even(4) is True, "is_even(4) should be True"
def test_prints():
    assert program_output.strip() == "ready", "print exactly 'ready'"
  </script>
  <details class="hint"><summary>Hint</summary><p>…</p></details>
  <details class="solution"><summary>Show solution</summary><pre><code class="language-python">…</code></pre></details>
</div>
```

- `data-id` must be unique across the site: `<module id>-e<n>` (for example `m09-e3`).
- Tests are `test_*` functions that run in the learner's namespace after their code. Every assert carries a helpful
  message. `program_output` holds everything the learner's code printed. `capture_output(func, *args, stdin=None)`
  returns `(result, printed_text)`. Tests must not contain `</script>`.
- Verify each solution passes its tests (paste both into `pixi run python` locally).

### Quizzes

```html
<div class="quiz" data-id="m09-quiz">
<script type="application/json">
{"title": "Functions quiz", "passScore": 0.7, "questions": [
  {"type": "single", "prompt": "HTML allowed", "code": "optional python shown above options", "options": ["a", "b"], "answer": 1, "explanation": "<p>Why.</p>"},
  {"type": "multi", "prompt": "…", "options": ["…", "…", "…"], "answer": [0, 2], "explanation": "…"},
  {"type": "output", "prompt": "What does this print?", "code": "print(1 + 1)", "answer": "2", "explanation": "…"},
  {"type": "text", "prompt": "Which keyword…?", "answer": ["def"], "explanation": "…"}
]}
</script>
</div>
```

The payload must be strict JSON (double quotes, no trailing commas, `\n` for newlines inside strings). `answer` is a
0-based index (`single`), a list of indexes (`multi`), or the exact text/accepted list (`output`/`text`; `text` is
case-insensitive). Every question needs an `explanation` that teaches, not just says "correct".

### Callouts, tags, and layout helpers

```html
<aside class="callout note|tip|warn|danger|pixi|pro|think"><p>…</p></aside>
<aside class="callout note" data-title="Custom heading"><p>…</p></aside>
<span class="tag pixi">pixi</span>
<div class="two-col">…</div>   <div class="card-grid"><div class="card"><h4>…</h4>…</div></div>
<div class="tabs"><div class="tab" data-label="Version A">…</div><div class="tab" data-label="Version B">…</div></div>
<details class="reveal"><summary>Reveal</summary>…</details>
<ul class="checklist" data-id="m09-mini">…</ul>          (persisted checkboxes; unique data-id)
<pre class="mermaid">flowchart LR; A-->B</pre>          (Mermaid diagrams)
<figure class="figure"><svg class="diagram" viewBox="…">…</svg><figcaption>…</figcaption></figure>
```

Inline SVG diagrams should use CSS variables for color (`fill="var(--viz-1)"`, `stroke="var(--fg-muted)"`) so they work
in light and dark themes.

### Project box

```html
<div class="project-box">
  <div class="widget-head"><span class="w-kind">Mini-project</span><span class="w-title">Title</span></div>
  <div class="widget-body"> spec, steps, <ul class="checklist" data-id="m09-mini">…</ul> </div>
</div>
```

### Visualizers

```html
<div class="viz" data-viz="NAME" data-config='{"key": "value"}'></div>
```

`data-config` is optional JSON. Available visualizers (`viz-agent.js`):

| Name | Purpose | Config (all optional) |
|---|---|---|
| `agent-loop` | Steps through the loop between your code, the model, and tools while the message list grows | `scenario`: `weather` \| `chain` \| `error` \| `runaway` |
| `token-meter` | Approximate tokens, share of the context window, and input cost for editable text | `text`, `calls`, `title` |

## fleetlab: the helper library exercises and lab checks use

Lesson cells and exercises `import fleetlab`. In the browser the package is injected into Pyodide from
`assets/js/fleetlab-src.js` (generated by `pixi run sync-runtime` from `src/fleetlab/`); locally it is installed in the
Pixi environment, so `pixi run check-exercises` and lab checks run exactly the same code. It never calls a model.
Read `reference/fleetlab.html` for the full API. The essentials:

```python
import fleetlab

spec = fleetlab.check_agent(text, "reviewer.md")       # .problems, .tools, .can_write(), .meta, .prompt
problems = fleetlab.check_skill(text, "add-command")   # list of strings
payload = fleetlab.pre_tool_use("Bash", {"command": "git push origin main"})
result = fleetlab.run_hook(main, payload)              # in-process: .exit_code, .stderr, .blocked, .decision, .reason
result = fleetlab.run_script(path, payload, cwd=..., env=...)   # subprocess, used by lab checks
run = fleetlab.parse_stream(stream_json_text)          # .calls, .result, .num_turns, .cost_usd, .calls_by_tool()
fleetlab.hook_commands(settings, "PreToolUse", "Bash") # which command hooks would run
```

Exercise solutions must import what they use (`import fleetlab`, `import json`): `check-exercises` runs the solution
on its own, without the starter.

## Labs

Labs live in `labs/<id>/` (`m02-lab1`) with `lab.toml` (`id`, `title`, `module`, optional `sample = true` to lay the
starter over `sample/`), `README.md` (the specification), `starter/`, and `tests/`. Lab checks use the `workspace`
fixture from `labs/conftest.py` (a staged copy under `build/labs/`) and `fleetlab`. Live checks take the `claude_cli`
fixture and skip unless graded with `--live`.

**Labs ship without reference solutions.** The README and the checks are the specification. `pixi run check-labs`
must show every untouched starter failing. When you write or change a lab, verify its checks against a throwaway
implementation outside the repository, and never commit that implementation. Every lab id must appear on its module
page.

## Facts about Claude Code to teach (and never contradict)

- Subagents: Markdown with YAML frontmatter in `.claude/agents/` (project) or `~/.claude/agents/` (user); only `name`
  and `description` are required; unknown fields are silently ignored. Fields: `tools`, `disallowedTools`, `model`
  (`sonnet`, `opus`, `haiku`, `fable`, a full id, or `inherit`), `permissionMode`, `isolation: worktree`, `maxTurns`,
  `autoCompactWindow`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `omitClaudeMd`, `effort`,
  `initialPrompt`, `color`. Managed and `--agents` definitions win over project, which wins over user.
- Hooks: configured under `"hooks"` → event → matcher group → handlers. Exit 0 continues; exit 2 blocks (stderr is
  the reason); any other code is a non-blocking error. Exit 1 does not block. PreToolUse JSON decisions go under
  `hookSpecificOutput.permissionDecision` (`allow`, `deny`, `ask`, `defer`); Stop uses `{"decision": "block",
  "reason": ...}`. Stop payloads carry `stop_hook_active`. Use `$CLAUDE_PROJECT_DIR` in commands. Default command
  timeout is 600 seconds.
- Matchers: empty or `*` matches all; letters, digits, `_`, `-`, spaces, commas, and `|` are exact names or lists;
  anything else is an unanchored regex. MCP tools are `mcp__<server>__<tool>`.
- Permission modes: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`. Rules
  `Bash(git diff *)`: the space before `*` matters; deny wins.
- Headless: `claude -p`, `--output-format text|json|stream-json` (stream-json with `--verbose`), `--allowedTools`,
  `--permission-mode`, `--max-turns`, `--json-schema` (→ `structured_output`), `--resume`, `--continue`, `--bare`
  (loads nothing it isn't told about; uses `ANTHROPIC_API_KEY`). Result events have `subtype`, `is_error`,
  `num_turns`, `total_cost_usd`, `session_id`, `result`.
- Skills: `.claude/skills/<name>/SKILL.md` in the open Agent Skills format; name matches the folder; progressive
  disclosure (metadata, body, linked files).
- CLAUDE.md loads from the home directory, the project, and subdirectories; `@file` imports. Recommend AGENTS.md plus a
  CLAUDE.md containing `@AGENTS.md` for multi-tool fleets.

When in doubt, check the current docs at https://code.claude.com/docs and link them from "Going further".

## Pixi conventions taught by the course

Pixi is the only tool learners use to install Python and packages, and to run code. Never tell the learner to use
`pip install`, `python -m venv`, `uv`, or bare `python`/`pytest` outside the environment. Lab commands are
`pixi run labs`, `pixi run start <lab>`, `pixi run grade <lab>`, and `pixi run grade-live <lab>`.
