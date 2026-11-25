from shelf import cli, store


def test_add_then_list(shelf_file, capsys):
    assert cli.main(["add", "Refactoring", "--author", "Fowler", "--year", "1999"]) == 0
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "Added: Refactoring — Fowler (1999)" in out
    assert out.strip().endswith("Refactoring — Fowler (1999)")
    assert len(store.load()) == 1


def test_search_reports_no_match(shelf_file, capsys):
    assert cli.main(["search", "nothing"]) == 0
    assert "No books found." in capsys.readouterr().out


def test_format_book_without_year():
    from shelf.models import Book

    assert cli.format_book(Book("Dune", "Herbert")) == "Dune — Herbert"
