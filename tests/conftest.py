import json
import logging

import httpx
import pytest

from explore_graphql_with_python.app import create_app
from explore_graphql_with_python.config import Settings


@pytest.fixture
def log() -> logging.Logger:
    return logging.getLogger("test")


@pytest.fixture
def data_file(tmp_path):
    path = tmp_path / "books.json"
    path.write_text(
        """[
  {"id": 1, "title": "The Great Gatsby", "genre": "fiction", "author": "F. Scott Fitzgerald"},
  {"id": 2, "title": "Dune", "genre": "sci-fi", "author": "Frank Herbert"}
]
"""
    )
    return path


@pytest.fixture
def large_data_file(tmp_path):
    path = tmp_path / "books.json"
    books = [{"id": i, "title": f"Book{i}"} for i in range(1, 14)]
    books.append(
        {
            "id": 14,
            "title": "Gatsby",
            "genre": "fiction",
            "author": "F. Scott Fitzgerald",
        }
    )
    path.write_text(json.dumps(books))
    return path


@pytest.fixture
async def client(data_file):
    app = create_app(Settings(data_path=str(data_file)))
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            follow_redirects=True,
        ) as http:
            yield http


@pytest.fixture
async def large_client(large_data_file):
    app = create_app(Settings(data_path=str(large_data_file)))
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            follow_redirects=True,
        ) as http:
            yield http
