import pytest

from explore_graphql_with_python.models import Book, Genre
from explore_graphql_with_python.repositories import (
    BookNotFoundError,
    JsonBookRepository,
)


async def test_load_from_file(data_file):
    repo = JsonBookRepository(data_file)
    books = await repo.get_all()
    assert [b.title for b in books] == ["The Great Gatsby", "Dune"]
    assert books[0].genre == Genre.FICTION
    assert books[1].genre == Genre.SCI_FI


async def test_get_by_id(data_file):
    repo = JsonBookRepository(data_file)
    book = await repo.get_by_id(1)
    assert book.title == "The Great Gatsby"
    assert book.author == "F. Scott Fitzgerald"


async def test_get_by_id_missing(data_file):
    repo = JsonBookRepository(data_file)
    with pytest.raises(BookNotFoundError):
        await repo.get_by_id(999)


async def test_list_by_genre(data_file):
    repo = JsonBookRepository(data_file)
    result = await repo.list_by_genre(Genre.SCI_FI)
    assert [b.title for b in result] == ["Dune"]


async def test_list_by_genre_none(data_file):
    repo = JsonBookRepository(data_file)
    result = await repo.list_by_genre(None)
    assert len(result) == 2


async def test_create_assigns_next_id(data_file):
    repo = JsonBookRepository(data_file)
    created = await repo.create(
        Book(id=0, title="New", genre=Genre.POETRY, author="X")
    )
    assert created.id == 3
    assert created.title == "New"


async def test_create_persists(data_file):
    repo = JsonBookRepository(data_file)
    await repo.create(Book(id=0, title="New"))
    reloaded = await repo.get_all()
    assert any(b.title == "New" for b in reloaded)


async def test_delete(data_file):
    repo = JsonBookRepository(data_file)
    assert await repo.delete(1) is True
    assert [b.title for b in await repo.get_all()] == ["Dune"]


async def test_delete_missing(data_file):
    repo = JsonBookRepository(data_file)
    with pytest.raises(BookNotFoundError):
        await repo.delete(999)
