from dataclasses import dataclass

from .book import Book


@dataclass
class BookPage:
    items: list[Book]
    total: int
