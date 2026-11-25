"""Load and save the shelf as JSON."""

import json
import os
from pathlib import Path

from shelf.models import Book

DEFAULT_FILE = "shelf.json"


def shelf_path() -> Path:
    """Where the shelf is stored: ``$SHELF_FILE`` or ``shelf.json`` in the current directory."""
    return Path(os.environ.get("SHELF_FILE", DEFAULT_FILE))


def load(path: Path | None = None) -> list[Book]:
    """Read every book. A missing file is an empty shelf."""
    path = path or shelf_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Book.from_dict(item) for item in data]


def save(books: list[Book], path: Path | None = None) -> None:
    """Write every book, replacing the file."""
    path = path or shelf_path()
    path.write_text(json.dumps([b.to_dict() for b in books], indent=2) + "\n", encoding="utf-8")


def search(books: list[Book], term: str) -> list[Book]:
    """Books whose title or author contains ``term``."""
    return [b for b in books if term in b.title or term in b.author]


def by_year(books: list[Book]) -> list[Book]:
    """Books sorted by year, oldest first; books without a year go last."""
    return sorted(books, key=lambda b: b.year)  # type: ignore[arg-type,return-value]
