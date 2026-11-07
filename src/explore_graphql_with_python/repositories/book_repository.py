from __future__ import annotations

import asyncio
import json
from pathlib import Path

from ..models import Book, Genre


class BookNotFoundError(LookupError):
    """Raised when a book cannot be found by its ID."""

    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book with id {book_id} not found")
        self.book_id = book_id


class JsonBookRepository:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    async def get_all(self) -> list[Book]:
        return await asyncio.to_thread(self._load)

    async def get_by_id(self, book_id: int) -> Book:
        for book in await self.get_all():
            if book.id == book_id:
                return book
        raise BookNotFoundError(book_id)

    async def list_by_genre(
        self, genre: Genre | None
    ) -> list[Book]:
        books = await self.get_all()
        if genre is not None:
            return [b for b in books if b.genre == genre]
        return books

    async def create(self, book: Book) -> Book:
        books = await self.get_all()
        next_id = max((b.id for b in books), default=0) + 1
        new_book = Book(
            id=next_id,
            title=book.title,
            genre=book.genre,
            author=book.author,
        )
        books.append(new_book)
        await asyncio.to_thread(self._save, books)
        return new_book

    async def delete(self, book_id: int) -> bool:
        books = await self.get_all()
        filtered = [b for b in books if b.id != book_id]
        if len(filtered) == len(books):
            raise BookNotFoundError(book_id)
        await asyncio.to_thread(self._save, filtered)
        return True

    def _load(self) -> list[Book]:
        if not self._path.exists():
            return []
        with self._path.open(encoding="utf-8") as handle:
            raw = json.load(handle)
        return [self._to_book(entry) for entry in raw]

    def _save(self, books: list[Book]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(
                [self._to_dict(book) for book in books],
                handle,
                indent=2,
            )

    @staticmethod
    def _to_book(entry: dict) -> Book:
        genre_raw = entry.get("genre")
        genre = Genre(genre_raw) if genre_raw is not None else None
        return Book(
            id=entry["id"],
            title=entry["title"],
            genre=genre,
            author=entry.get("author"),
        )

    @staticmethod
    def _to_dict(book: Book) -> dict:
        data: dict = {"id": book.id, "title": book.title}
        if book.genre is not None:
            data["genre"] = book.genre.value
        if book.author is not None:
            data["author"] = book.author
        return data
