import logging

import pytest

from explore_graphql_with_python.models import Book, Genre
from explore_graphql_with_python.repositories import (
    BookNotFoundError,
    JsonBookRepository,
)
from support import step, verify, verify_true


async def test_load_from_file(data_file, log: logging.Logger):
    """The repository loads all books from the JSON file."""
    repo = JsonBookRepository(data_file)
    step(log, "get_all() from JSON file")
    books = await repo.get_all()
    verify(log, "titles", [b.title for b in books], ["The Great Gatsby", "Dune"])
    verify(log, "first genre", books[0].genre, Genre.FICTION)
    verify(log, "second genre", books[1].genre, Genre.SCI_FI)


async def test_get_by_id(data_file, log: logging.Logger):
    """The repository returns a book by its ID."""
    repo = JsonBookRepository(data_file)
    step(log, "get_by_id(1)")
    book = await repo.get_by_id(1)
    verify(log, "title", book.title, "The Great Gatsby")
    verify(log, "author", book.author, "F. Scott Fitzgerald")


async def test_get_by_id_missing(data_file, log: logging.Logger):
    """The repository raises for a missing book ID."""
    repo = JsonBookRepository(data_file)
    step(log, "get_by_id(999) -> expect BookNotFoundError")
    with pytest.raises(BookNotFoundError):
        await repo.get_by_id(999)


async def test_list_by_genre(data_file, log: logging.Logger):
    """The repository filters books by genre."""
    repo = JsonBookRepository(data_file)
    step(log, "list_by_genre(SCI_FI)")
    result = await repo.list_by_genre(Genre.SCI_FI)
    verify(log, "titles", [b.title for b in result], ["Dune"])


async def test_list_by_genre_none(data_file, log: logging.Logger):
    """The repository returns all books when genre is None."""
    repo = JsonBookRepository(data_file)
    step(log, "list_by_genre(None)")
    result = await repo.list_by_genre(None)
    verify(log, "count", len(result), 2)


async def test_create_assigns_next_id(data_file, log: logging.Logger):
    """The repository assigns the next sequential ID on create."""
    repo = JsonBookRepository(data_file)
    step(log, "create(New, POETRY, X)")
    created = await repo.create(
        Book(id=0, title="New", genre=Genre.POETRY, author="X")
    )
    verify(log, "assigned id", created.id, 3)
    verify(log, "title", created.title, "New")


async def test_create_persists(data_file, log: logging.Logger):
    """A created book is persisted to the JSON file."""
    repo = JsonBookRepository(data_file)
    step(log, "create(New)")
    await repo.create(Book(id=0, title="New"))
    step(log, "reload get_all()")
    reloaded = await repo.get_all()
    verify_true(log, "persisted", any(b.title == "New" for b in reloaded))


async def test_delete(data_file, log: logging.Logger):
    """The repository deletes a book by ID."""
    repo = JsonBookRepository(data_file)
    step(log, "delete(1)")
    verify(log, "delete result", await repo.delete(1), True)
    step(log, "reload get_all()")
    verify(log, "remaining titles", [b.title for b in await repo.get_all()], ["Dune"])


async def test_delete_missing(data_file, log: logging.Logger):
    """The repository raises when deleting a missing book."""
    repo = JsonBookRepository(data_file)
    step(log, "delete(999) -> expect BookNotFoundError")
    with pytest.raises(BookNotFoundError):
        await repo.delete(999)
