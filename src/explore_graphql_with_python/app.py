from __future__ import annotations

from contextlib import asynccontextmanager

from ariadne.asgi import GraphQL
from fastapi import FastAPI

from .config import Settings
from .graphql import build_schema, get_context_value
from .repositories import JsonBookRepository
from .services import BookService


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository = JsonBookRepository(settings.data_path)
        app.state.book_repository = repository
        app.state.book_service = BookService(repository)
        yield

    app = FastAPI(
        title="Book Store GraphQL API",
        version="1.0.0",
        lifespan=lifespan,
    )

    schema = build_schema()
    graphql_app = GraphQL(
        schema,
        context_value=get_context_value,
        debug=settings.debug,
    )
    app.mount("/graphql", graphql_app)

    return app
