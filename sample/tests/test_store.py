from shelf import store
from shelf.models import Book


def test_missing_file_is_empty(shelf_file):
    assert store.load() == []


def test_save_then_load_round_trips(shelf_file, books):
    store.save(books)
    assert store.load() == books


def test_search_matches_title(books):
    assert [b.title for b in store.search(books, "Refactor")] == ["Refactoring"]


def test_search_matches_author(books):
    assert [b.title for b in store.search(books, "Forsgren")] == ["Accelerate"]


def test_by_year_sorts_oldest_first():
    books = [Book("B", year=2018), Book("A", year=1999)]
    assert [b.title for b in store.by_year(books)] == ["A", "B"]
