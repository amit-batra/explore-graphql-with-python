from __future__ import annotations

from ..models import Book, BookPage, Genre
from ..repositories import JsonBookRepository

DEFAULT_PAGE_SIZE = 10


class BookService:
    def __init__(self, repository: JsonBookRepository) -> None:
        self.repository = repository

    async def get_book(self, book_id: int) -> Book:
        return await self.repository.get_by_id(book_id)

    async def list_books(
        self, genre: Genre | None, page: int
    ) -> BookPage:
        books = await self.repository.list_by_genre(genre)
        total = len(books)
        start = (page - 1) * DEFAULT_PAGE_SIZE
        end = start + DEFAULT_PAGE_SIZE
        items = books[start:end]
        return BookPage(items=items, total=total)

    async def create_book(
        self,
        title: str,
        genre: Genre | None = None,
        author: str | None = None,
    ) -> Book:
        return await self.repository.create(
            Book(id=0, title=title, genre=genre, author=author)
        )

    async def delete_book(self, book_id: int) -> bool:
        return await self.repository.delete(book_id)
