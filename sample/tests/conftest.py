import pytest

from shelf.models import Book


@pytest.fixture
def books() -> list[Book]:
    return [
        Book("Refactoring", "Fowler", 1999, ["classic"]),
        Book("The Pragmatic Programmer", "Hunt, Thomas", 1999),
        Book("Accelerate", "Forsgren", 2018, ["devops"]),
    ]


@pytest.fixture
def shelf_file(tmp_path, monkeypatch):
    path = tmp_path / "shelf.json"
    monkeypatch.setenv("SHELF_FILE", str(path))
    return path
