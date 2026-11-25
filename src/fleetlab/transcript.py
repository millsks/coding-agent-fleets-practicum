"""Read the newline-delimited JSON that ``claude -p --output-format stream-json --verbose`` prints.

Each line is one event. The ones that matter for reading a run:

* ``{"type": "system", "subtype": "init", ...}``: session id, model, and the tools available.
* ``{"type": "assistant", "message": {"content": [...]}}``: text and ``tool_use`` blocks the model produced.
* ``{"type": "user", "message": {"content": [...]}}``: ``tool_result`` blocks sent back to the model.
* ``{"type": "result", ...}``: the last line, with ``subtype``, ``num_turns``, ``total_cost_usd``, and ``result``.

Messages from subagents carry the id of the tool call that started them in ``parent_tool_use_id``; messages from the
main conversation carry ``null``.
"""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """One tool call and what came back.

    Attributes:
        id: The ``tool_use`` block id.
        name: Tool name, such as ``Bash`` or ``Agent``.
        input: The arguments the model sent.
        parent: ``parent_tool_use_id`` of the message, or ``None`` for the main conversation.
        result: Text of the matching ``tool_result``, or ``None`` if none arrived.
        is_error: Whether the result was an error.
    """

    id: str
    name: str
    input: dict[str, Any]
    parent: str | None = None
    result: str | None = None
    is_error: bool = False


@dataclass
class Run:
    """A parsed headless run.

    Attributes:
        session_id: Session id from the init event.
        model: Model from the init event.
        tools: Tools the session had.
        calls: Every tool call in order, including subagents'.
        texts: Text the main conversation produced, in order.
        result: The final ``result`` event, or ``None`` if the stream ended early.
    """

    session_id: str = ""
    model: str = ""
    tools: list[str] = field(default_factory=list)
    calls: list[ToolCall] = field(default_factory=list)
    texts: list[str] = field(default_factory=list)
    result: dict[str, Any] | None = None

    @property
    def finished(self) -> bool:
        """Whether the stream reached its ``result`` event."""
        return self.result is not None

    @property
    def succeeded(self) -> bool:
        """Whether the run ended with ``subtype == "success"`` and no error flag."""
        result = self.result or {}
        return result.get("subtype") == "success" and not result.get("is_error")

    @property
    def num_turns(self) -> int:
        """Agentic turns reported by the result event (0 if unfinished)."""
        return int((self.result or {}).get("num_turns", 0))

    @property
    def cost_usd(self) -> float:
        """Estimated cost reported by the result event (0.0 if unfinished)."""
        return float((self.result or {}).get("total_cost_usd", 0.0))

    def calls_by_tool(self) -> dict[str, int]:
        """Count tool calls per tool name."""
        counts: dict[str, int] = {}
        for call in self.calls:
            counts[call.name] = counts.get(call.name, 0) + 1
        return counts


def _result_text(block: dict[str, Any]) -> str:
    content = block.get("content", "")
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return str(content)


def parse_stream(text: str) -> Run:
    """Parse a stream-json transcript.

    Blank lines and lines that are not JSON objects are skipped, so a transcript with stray log lines still parses.

    Args:
        text: The whole transcript.

    Returns:
        The parsed run.
    """
    run = Run()
    by_id: dict[str, ToolCall] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            run.session_id = str(event.get("session_id", ""))
            run.model = str(event.get("model", ""))
            run.tools = [str(t) for t in event.get("tools", [])]
        elif kind in ("assistant", "user"):
            parent = event.get("parent_tool_use_id")
            content = (event.get("message") or {}).get("content", [])
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    call = ToolCall(
                        str(block.get("id", "")), str(block.get("name", "")), dict(block.get("input", {})), parent
                    )
                    run.calls.append(call)
                    by_id[call.id] = call
                elif block.get("type") == "tool_result" and block.get("tool_use_id") in by_id:
                    call = by_id[block["tool_use_id"]]
                    call.result = _result_text(block)
                    call.is_error = bool(block.get("is_error"))
                elif block.get("type") == "text" and kind == "assistant" and parent is None:
                    run.texts.append(str(block.get("text", "")))
        elif kind == "result":
            run.result = event
    return run
