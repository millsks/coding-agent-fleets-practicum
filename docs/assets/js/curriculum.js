/* Curriculum manifest. The object below must stay valid JSON: practicum check-site parses it. */
window.CURRICULUM = {
  "title": "Coding Agent Fleets Practicum",
  "python": "3.14",
  "parts": [
    {
      "id": "part0",
      "number": 0,
      "title": "Orientation",
      "level": "Start here",
      "summary": "What a fleet of coding agents is, how this practicum works, the shelf sample project, labs graded with Pixi, and working safely.",
      "modules": [
        {
          "id": "m00",
          "title": "How This Practicum Works",
          "href": "modules/m00-orientation.html",
          "minutes": 60,
          "summary": "The fleet you will build, fleetlab in the browser, labs and grading, the shelf sample project, and safety rules for agents."
        }
      ],
      "projects": []
    },
    {
      "id": "part1",
      "number": 1,
      "title": "Stage 1 · One Agent",
      "level": "Level 1 · Builder",
      "summary": "Understand the harness around the model, then write one good agent: its definition, the context it reads, and the hooks that enforce its rules.",
      "modules": [
        {
          "id": "m01",
          "title": "The Harness",
          "href": "modules/m01-the-harness.html",
          "minutes": 120,
          "summary": "Agent = model + harness. The loop inside Claude Code, tools and permissions, settings, headless runs, and reading a transcript."
        },
        {
          "id": "m02",
          "title": "Writing a Subagent",
          "href": "modules/m02-writing-a-subagent.html",
          "minutes": 150,
          "summary": "Subagent files, every frontmatter field, descriptions that trigger delegation, prompts with stop conditions, and least-privilege tools."
        },
        {
          "id": "m03",
          "title": "Context Engineering",
          "href": "modules/m03-context-engineering.html",
          "minutes": 120,
          "summary": "What loads at startup, AGENTS.md and CLAUDE.md, skills and progressive disclosure, and spending the context window on the task."
        },
        {
          "id": "m04",
          "title": "Hooks and Gates",
          "href": "modules/m04-hooks-and-gates.html",
          "minutes": 150,
          "summary": "Hook events, payloads, exit codes and JSON decisions, matchers, a guard for risky commands, and a Stop gate that keeps the agent working until checks pass."
        }
      ],
      "projects": []
    }
  ],
  "reference": [
    {
      "id": "ref-roadmap",
      "title": "Roadmap",
      "href": "reference/roadmap.html",
      "summary": "Stage 2 (many agents), the capstone, and Levels 2-3."
    },
    {
      "id": "ref-fleetlab",
      "title": "fleetlab Reference",
      "href": "reference/fleetlab.html",
      "summary": "Every fleetlab helper used in lessons and lab checks: frontmatter, agents, skills, hooks, settings, and transcripts."
    },
    {
      "id": "ref-cheatsheet",
      "title": "Agent and Hook Cheat Sheet",
      "href": "reference/cheatsheet.html",
      "summary": "Subagent fields, hook events and exit codes, permission modes, and headless flags on one page."
    },
    {
      "id": "ref-glossary",
      "title": "Glossary",
      "href": "reference/glossary.html",
      "summary": "Terms used in the course, with links to where each is taught."
    }
  ]
};
