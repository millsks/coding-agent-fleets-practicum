"""fleetlab: small, dependency-free helpers for learning to write and check coding agents.

The same package runs in your browser (Pyodide) for lesson exercises and on your machine for lab checks. It never
calls a model. It reads and checks the files that configure agents, builds the JSON payloads that Claude Code sends
to hooks, runs hook code against them, and reads the transcripts that headless runs produce.
"""

from fleetlab.agents import KNOWN_FIELDS, KNOWN_TOOLS, READ_ONLY_TOOLS, WRITE_TOOLS, AgentSpec, check_agent, load_agent
from fleetlab.context import estimate_tokens
from fleetlab.frontmatter import Document, FrontmatterError, parse
from fleetlab.hooks import HookResult, pre_tool_use, run_hook, run_script, stop
from fleetlab.settings import hook_commands, matcher_matches
from fleetlab.skills import check_skill
from fleetlab.transcript import Run, ToolCall, parse_stream

__all__ = [
    "KNOWN_FIELDS",
    "KNOWN_TOOLS",
    "READ_ONLY_TOOLS",
    "WRITE_TOOLS",
    "AgentSpec",
    "Document",
    "FrontmatterError",
    "HookResult",
    "Run",
    "ToolCall",
    "check_agent",
    "check_skill",
    "estimate_tokens",
    "hook_commands",
    "load_agent",
    "matcher_matches",
    "parse",
    "parse_stream",
    "pre_tool_use",
    "run_hook",
    "run_script",
    "stop",
]

__version__ = "0.1.0"
