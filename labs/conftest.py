"""Shared fixtures for lab checks.

``pixi run grade <lab>`` copies your workspace to ``build/labs/<lab>/`` and sets ``PRACTICUM_SRC`` to that copy, so
checks can read and run your files without ever changing ``work/``.
"""

import os
import shutil
from pathlib import Path

import pytest

_source = os.environ.get("PRACTICUM_SRC")
if _source is None:
    raise RuntimeError("Run lab checks with `pixi run grade <lab>` so PRACTICUM_SRC is set.")

LIVE = os.environ.get("PRACTICUM_LIVE") == "1"


@pytest.fixture
def workspace() -> Path:
    """The staged copy of the workspace being graded."""
    return Path(_source).resolve()


@pytest.fixture
def claude_cli() -> str:
    """Path to the real ``claude`` CLI for live checks; skips unless grading with ``--live`` and it is installed."""
    if not LIVE:
        pytest.skip("live check: run `pixi run grade-live <lab>` to call the real claude CLI")
    found = shutil.which("claude")
    if found is None:
        pytest.skip("live check: the claude CLI is not on PATH")
    return found
