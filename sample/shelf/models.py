"""The Book record."""

from dataclasses import asdict, dataclass, field


@dataclass
class Book:
    """One book on the shelf.

    Attributes:
        title: The book's title.
        author: Author name as the user typed it.
        year: Year of publication, if known.
        tags: Free-form labels such as ``"to-read"``.
    """

    title: str
    author: str = ""
    year: int | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Serialise for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Book":
        """Build a book from stored JSON."""
        year = data.get("year")
        return cls(
            title=str(data["title"]),
            author=str(data.get("author", "")),
            year=int(year) if year is not None else None,  # type: ignore[call-overload]
            tags=[str(t) for t in data.get("tags", [])],  # type: ignore[attr-defined]
        )
