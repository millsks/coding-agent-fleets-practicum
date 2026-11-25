"""Command-line interface: ``python -m shelf add|list|search``."""

import argparse
from collections.abc import Sequence

from shelf import store
from shelf.models import Book


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(prog="shelf", description="Track the books on your shelf.")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add a book")
    add.add_argument("title")
    add.add_argument("--author", default="")
    add.add_argument("--year", type=int)
    add.add_argument("--tag", action="append", default=[], dest="tags")

    listing = commands.add_parser("list", help="list books")
    listing.add_argument("--by-year", action="store_true", help="sort by publication year")

    find = commands.add_parser("search", help="find books by title or author")
    find.add_argument("term")
    return parser


def format_book(book: Book) -> str:
    """One line per book: ``Title — Author (Year)``."""
    line = book.title
    if book.author:
        line += f" — {book.author}"
    if book.year:
        line += f" ({book.year})"
    return line


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return an exit code."""
    args = build_parser().parse_args(argv)
    books = store.load()
    if args.command == "add":
        books.append(Book(args.title, args.author, args.year, args.tags))
        store.save(books)
        print(f"Added: {format_book(books[-1])}")
        return 0
    if args.command == "list":
        shown = store.by_year(books) if args.by_year else books
    else:
        shown = store.search(books, args.term)
    for book in shown:
        print(format_book(book))
    if not shown:
        print("No books found.")
    return 0
