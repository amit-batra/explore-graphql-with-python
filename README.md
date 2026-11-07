# Explore GraphQL with Python

A schema-first Python GraphQL microservice for a Book Store API, built from the
SDL contract in [`schema/schema.graphql`](schema/schema.graphql).

## Architecture

The service uses a layered architecture. GraphQL resolvers are thin adapters;
all business logic lives in the application layer, which is independent of
Ariadne and HTTP.

```
src/explore_graphql_with_python/
├── config.py             # Settings (pydantic-settings, env-configurable)
├── app.py                # FastAPI app + lifespan + Ariadne ASGI mount
├── __main__.py           # `python -m` / script entry point
├── models/               # Domain models (Book, BookPage, Genre)
├── repositories/         # Persistence abstraction (JSON file store)
│   └── book_repository.py
├── services/             # Application layer (business logic)
│   ├── book_service.py
│   └── health_service.py
└── graphql/              # GraphQL API layer
    ├── schema.py         # Loads SDL, builds executable schema
    ├── enum_types.py     # Genre enum binding
    ├── queries.py        # Query resolvers
    ├── mutations.py      # Mutation resolvers
    └── context.py        # Request-scoped dependency injection
```

## API

| Operation            | Description                                  |
| -------------------- | -------------------------------------------- |
| `Query.health`       | Public liveness probe (`HealthStatusResponse`)|
| `Query.books`        | Paginated books, optional `genre` filter      |
| `Query.book`         | Book by ID                                   |
| `Mutation.createBook`| Create a book (server assigns the ID)        |
| `Mutation.deleteBook`| Delete a book; missing ID yields a `NOT_FOUND` error |

The `Genre` enum (`FICTION`, `NONFICTION`, `SCI_FI`, `POETRY`) maps to the REST
values `fiction`, `nonfiction`, `sci-fi`, `poetry` on the persistence layer.

## Persistence

Books are persisted in a JSON file (`data/books.json` by default, configurable
via `APP_DATA_PATH`). The `JsonBookRepository` performs all file I/O in worker
threads so resolvers stay non-blocking.

## Running locally

```bash
uv sync
uv run uvicorn "explore_graphql_with_python.app:create_app" --factory
# or:
uv run python -m explore_graphql_with_python
```

The GraphQL endpoint is mounted at `/graphql/` (FastAPI redirects `/graphql` to
it). A GraphiQL explorer is available at `GET /graphql/` in development.

### Example requests

```bash
# Health
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ health { status } }"}'

# List books, filtered by genre
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ books(genre: SCI_FI, page: 1) { items { id title } total } }"}'

# Create a book
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { createBook(input: {title: \"New\", genre: POETRY}) { id title genre } }"}'
```

## Testing

```bash
uv run pytest
uv run ruff check src tests
```

Tests cover the repository (unit), the service layer (unit), and the full
GraphQL API over HTTP (integration), using a temporary data file so the seed
data is never mutated.

## Configuration

All settings are read from environment variables (see `.env.example`):

| Variable          | Default            | Description                  |
| ----------------- | ------------------ | ---------------------------- |
| `APP_DATA_PATH`   | `data/books.json`  | Path to the books data file  |
| `APP_HOST`        | `127.0.0.1`        | Server bind host             |
| `APP_PORT`        | `8000`             | Server bind port             |
| `APP_DEBUG`       | `false`            | Enables GraphiQL/debug mode  |
