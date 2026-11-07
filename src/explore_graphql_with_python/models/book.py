from dataclasses import dataclass

from .genre import Genre


@dataclass
class Book:
    id: int
    title: str
    genre: Genre | None = None
    author: str | None = None
