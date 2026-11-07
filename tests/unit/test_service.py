import pytest

from explore_graphql_with_python.models import Genre
from explore_graphql_with_python.repositories import (
    BookNotFoundError,
    JsonBookRepository,
)
from explore_graphql_with_python.services import BookService, get_health


@pytest.fixture
def repo(data_file):
    return JsonBookRepository(data_file)


async def test_get_health():
    response = get_health()
    assert response.status == "OK"


async def test_get_book(repo):
    service = BookService(repo)
    book = await service.get_book(1)
    assert book.title == "The Great Gatsby"
    assert book.genre == Genre.FICTION


async def test_get_book_missing_raises(repo):
    service = BookService(repo)
    with pytest.raises(BookNotFoundError):
        await service.get_book(999)


async def test_list_books_pagination(repo):
    service = BookService(repo)
    page = await service.list_books(None, 1)
    assert page.total == 2
    assert len(page.items) == 2


async def test_list_books_pagination_beyond_range(repo):
    service = BookService(repo)
    page = await service.list_books(None, 3)
    assert page.total == 2
    assert page.items == []


async def test_list_books_genre_filter(repo):
    service = BookService(repo)
    page = await service.list_books(Genre.SCI_FI, 1)
    assert [b.title for b in page.items] == ["Dune"]
    assert page.total == 1


async def test_list_books_genre_filter_no_matches(repo):
    service = BookService(repo)
    page = await service.list_books(Genre.POETRY, 1)
    assert page.total == 0
    assert page.items == []


async def test_create_book(repo):
    service = BookService(repo)
    created = await service.create_book("New", Genre.POETRY, "X")
    assert created.id == 3
    assert created.title == "New"
    assert created.genre == Genre.POETRY


async def test_create_book_minimal(repo):
    service = BookService(repo)
    created = await service.create_book("Solo")
    assert created.id == 3
    assert created.title == "Solo"
    assert created.genre is None
    assert created.author is None


async def test_delete_book(repo):
    service = BookService(repo)
    assert await service.delete_book(1) is True
    page = await service.list_books(None, 1)
    assert [b.title for b in page.items] == ["Dune"]


async def test_delete_book_missing_raises(repo):
    service = BookService(repo)
    with pytest.raises(BookNotFoundError):
        await service.delete_book(999)
