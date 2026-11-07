import logging

import pytest

from explore_graphql_with_python.models import Genre
from explore_graphql_with_python.repositories import (
    BookNotFoundError,
    JsonBookRepository,
)
from explore_graphql_with_python.services import BookService, get_health
from support import step, verify


@pytest.fixture
def repo(data_file):
    return JsonBookRepository(data_file)


async def test_get_health(log: logging.Logger):
    """The health service reports an OK status."""
    step(log, "get_health()")
    response = get_health()
    verify(log, "status", response.status, "OK")


async def test_get_book(repo, log: logging.Logger):
    """The service returns a book by its ID."""
    service = BookService(repo)
    step(log, "get_book(1)")
    book = await service.get_book(1)
    verify(log, "title", book.title, "The Great Gatsby")
    verify(log, "genre", book.genre, Genre.FICTION)


async def test_get_book_missing_raises(repo, log: logging.Logger):
    """The service raises for a missing book ID."""
    service = BookService(repo)
    step(log, "get_book(999) -> expect BookNotFoundError")
    with pytest.raises(BookNotFoundError):
        await service.get_book(999)


async def test_list_books_pagination(repo, log: logging.Logger):
    """The service paginates books, page 1."""
    service = BookService(repo)
    step(log, "list_books(None, page=1)")
    page = await service.list_books(None, 1)
    verify(log, "total", page.total, 2)
    verify(log, "items count", len(page.items), 2)


async def test_list_books_pagination_beyond_range(repo, log: logging.Logger):
    """The service returns an empty page beyond the last page."""
    service = BookService(repo)
    step(log, "list_books(None, page=3) -> expect empty")
    page = await service.list_books(None, 3)
    verify(log, "total", page.total, 2)
    verify(log, "items", page.items, [])


async def test_list_books_genre_filter(repo, log: logging.Logger):
    """The service filters books by genre."""
    service = BookService(repo)
    step(log, "list_books(SCI_FI, page=1)")
    page = await service.list_books(Genre.SCI_FI, 1)
    verify(log, "titles", [b.title for b in page.items], ["Dune"])
    verify(log, "total", page.total, 1)


async def test_list_books_genre_filter_no_matches(repo, log: logging.Logger):
    """The service returns an empty page when a genre matches nothing."""
    service = BookService(repo)
    step(log, "list_books(POETRY, page=1) -> expect empty")
    page = await service.list_books(Genre.POETRY, 1)
    verify(log, "total", page.total, 0)
    verify(log, "items", page.items, [])


async def test_create_book(repo, log: logging.Logger):
    """The service creates a book with a server-assigned ID."""
    service = BookService(repo)
    step(log, "create_book(New, POETRY, X)")
    created = await service.create_book("New", Genre.POETRY, "X")
    verify(log, "assigned id", created.id, 3)
    verify(log, "title", created.title, "New")
    verify(log, "genre", created.genre, Genre.POETRY)


async def test_create_book_minimal(repo, log: logging.Logger):
    """The service creates a book with a title only."""
    service = BookService(repo)
    step(log, "create_book(Solo)")
    created = await service.create_book("Solo")
    verify(log, "assigned id", created.id, 3)
    verify(log, "title", created.title, "Solo")
    verify(log, "genre", created.genre, None)
    verify(log, "author", created.author, None)


async def test_delete_book(repo, log: logging.Logger):
    """The service deletes a book by ID."""
    service = BookService(repo)
    step(log, "delete_book(1)")
    verify(log, "delete result", await service.delete_book(1), True)
    step(log, "list_books(None, page=1)")
    page = await service.list_books(None, 1)
    verify(log, "remaining titles", [b.title for b in page.items], ["Dune"])


async def test_delete_book_missing_raises(repo, log: logging.Logger):
    """The service raises when deleting a missing book."""
    service = BookService(repo)
    step(log, "delete_book(999) -> expect BookNotFoundError")
    with pytest.raises(BookNotFoundError):
        await service.delete_book(999)
