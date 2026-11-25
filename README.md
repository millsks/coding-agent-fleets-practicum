# coding-agent-fleets-practicum

An interactive course on writing coding agents yourself and orchestrating them into a fleet that covers the software
development lifecycle: triage, plan, build, test, review, release, heal, and learn. It uses Claude Code and the Claude
Agent SDK, and teaches the patterns (AGENTS.md, Agent Skills, hooks) that carry over to GitHub Copilot and Devin.

You write every agent definition, hook, and orchestration script. The course explains the ideas, drills them with
exercises in the browser, and checks your work in labs. It never hands you a finished fleet.

[![CI](https://github.com/millsks/coding-agent-fleets-practicum/actions/workflows/ci.yml/badge.svg)](https://github.com/millsks/coding-agent-fleets-practicum/actions/workflows/ci.yml)
![pixi](https://img.shields.io/badge/managed%20by-pixi-orange)

## What's inside

- **Level 1 · Builder, Stage 1 (One Agent):** an orientation module and four modules: the harness around the model,
  writing a subagent, context engineering, and hooks and gates. Each has runnable cells, graded exercises, a quiz,
  flashcards, and labs. Published as static HTML in [`docs/`](docs/).
- **Stage 2 (Many Agents)** and the capstone (a small fleet for the sample project) are next on the
  [roadmap](docs/reference/roadmap.html).
- **fleetlab** ([`src/fleetlab/`](src/fleetlab/)): a small, dependency-free library that checks agent and skill files,
  builds the JSON payloads Claude Code sends to hooks, runs hook code against them, and reads `stream-json`
  transcripts. It runs in the browser (Pyodide) for exercises and locally for lab checks. It never calls a model.
- **Labs** ([`labs/`](labs/)): a README specification, a starter workspace, and checks. **Labs ship without
  solutions**; CI proves every untouched starter fails its checks, so a passing grade means you built it. Most checks
  are deterministic and need no API key; optional live checks run your agents with the real `claude` CLI.
- **shelf** ([`sample/`](sample/)): the small book-tracking CLI every lab works on, with tests, real bugs, and five
  open issues (one of them a prompt injection).

## Installation

Install [Pixi](https://pixi.sh), then:

```sh
git clone https://github.com/millsks/coding-agent-fleets-practicum.git
cd coding-agent-fleets-practicum
pixi install
pixi run bootstrap      # pre-commit hooks (only needed if you contribute)
```

For live checks and for trying your agents interactively, install Claude Code by following the
[official setup guide](https://code.claude.com/docs/en/overview).

## Quick start

```sh
pixi run serve              # opens the course at http://127.0.0.1:8000/
```

Start with **Module 00: How This Practicum Works**. Each module ends with labs:

```sh
pixi run labs               # list labs and whether you've started them
pixi run start m02-lab1     # copy the starter into work/m02-lab1/
# read labs/m02-lab1/README.md and do the work in work/m02-lab1/
pixi run grade m02-lab1     # run the lab's checks against a copy of your work
pixi run grade-live m02-lab1  # optional: also run checks that call the real claude CLI
```

Grading copies your workspace to `build/labs/<lab>/`, so checks never modify `work/`.

## Development

```sh
pixi run test               # unit tests (fast)
pixi run cov                # all tests with a coverage gate (>= 90% of src/)
pixi run test-integration   # site, exercises, labs, bundle, and runtime checks
pixi run check-site         # links, anchors, quizzes, and exercise blocks in docs/
pixi run check-exercises    # every in-page exercise's reference answer passes its tests
pixi run check-labs         # every lab's untouched starter fails its checks
pixi run sync-runtime       # regenerate docs/assets/js/fleetlab-src.js after changing src/fleetlab/
pixi run bundle             # build the single-file edition: dist/coding-agent-fleets-practicum.html
pixi run ci                 # everything CI runs
```

Lesson and lab authors should read [`docs/AUTHORING.md`](docs/AUTHORING.md).

## License

[MIT](LICENSE)
