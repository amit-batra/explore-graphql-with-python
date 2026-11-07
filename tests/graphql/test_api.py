import logging

from support import step, verify, verify_false, verify_true


async def test_health_query(client, log: logging.Logger):
    """Health query returns the OK liveness status."""
    step(log, "POST /graphql { health { status } }")
    response = await client.post(
        "/graphql",
        json={"query": "{ health { status } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 200)
    verify(log, "response", payload, {"data": {"health": {"status": "OK"}}})


async def test_books_query(client, log: logging.Logger):
    """Books query returns all books with a total count."""
    step(log, "POST /graphql { books { items total } }")
    response = await client.post(
        "/graphql",
        json={"query": "{ books { items { id title genre author } total } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 200)
    verify(log, "total", payload["data"]["books"]["total"], 2)
    verify(
        log,
        "first item title",
        payload["data"]["books"]["items"][0]["title"],
        "The Great Gatsby",
    )
    verify(log, "second item genre", payload["data"]["books"]["items"][1]["genre"], "SCI_FI")


async def test_books_query_genre_filter(client, log: logging.Logger):
    """Books query filters by genre."""
    step(log, "POST /graphql { books(genre: SCI_FI) { items total } }")
    response = await client.post(
        "/graphql",
        json={"query": "{ books(genre: SCI_FI) { items { id title } total } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 200)
    verify(log, "total", payload["data"]["books"]["total"], 1)
    verify(log, "first item title", payload["data"]["books"]["items"][0]["title"], "Dune")


async def test_book_query(client, log: logging.Logger):
    """Book query returns a single book by ID."""
    step(log, "POST /graphql { book(id: 1) { id title genre author } }")
    response = await client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id title genre author } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 200)
    verify(log, "book title", payload["data"]["book"]["title"], "The Great Gatsby")


async def test_book_query_missing(client, log: logging.Logger):
    """Book query for a missing ID produces a GraphQL error."""
    step(log, "POST /graphql { book(id: 999) } -> expect error")
    response = await client.post(
        "/graphql",
        json={"query": "{ book(id: 999) { id title } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 400)
    verify(log, "data", payload["data"], None)
    verify_true(log, "error message present", bool(payload["errors"][0]["message"]))


async def test_create_book_mutation(client, log: logging.Logger):
    """CreateBook mutation assigns a server-side ID."""
    step(log, "POST /graphql mutation createBook(New, POETRY, X)")
    response = await client.post(
        "/graphql",
        json={
            "query": (
                "mutation { createBook(input: {title: \"New\", "
                "genre: POETRY, author: \"X\"}) { id title genre author } }"
            ),
        },
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 200)
    created = payload["data"]["createBook"]
    verify(log, "created title", created["title"], "New")
    verify(log, "created genre", created["genre"], "POETRY")
    verify(log, "created id", created["id"], 3)


async def test_delete_book_mutation(client, log: logging.Logger):
    """DeleteBook mutation returns True on success."""
    step(log, "POST /graphql mutation deleteBook(1)")
    response = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 1) }"},
    )
    verify(log, "status code", response.status_code, 200)
    verify(log, "response", response.json(), {"data": {"deleteBook": True}})


async def test_delete_book_missing_returns_not_found(client, log: logging.Logger):
    """DeleteBook on a missing ID produces a NOT_FOUND error."""
    step(log, "POST /graphql mutation deleteBook(999) -> expect NOT_FOUND")
    response = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 999) }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 400)
    verify(log, "data", payload["data"], None)
    verify(log, "error code", payload["errors"][0]["extensions"]["code"], "NOT_FOUND")


async def test_create_then_read(client, log: logging.Logger):
    """A created book is readable by its assigned ID."""
    step(log, "POST /graphql mutation createBook(Added)")
    create = await client.post(
        "/graphql",
        json={
            "query": (
                "mutation { createBook(input: {title: \"Added\"}) "
                "{ id title } }"
            ),
        },
    )
    verify(log, "create status code", create.status_code, 200)
    book_id = create.json()["data"]["createBook"]["id"]
    step(log, f"POST /graphql {{ book(id: {book_id}) }}")
    read = await client.post(
        "/graphql",
        json={"query": f"{{ book(id: {book_id}) {{ id title }} }}"},
    )
    verify(log, "read status code", read.status_code, 200)
    verify(log, "read title", read.json()["data"]["book"]["title"], "Added")


async def test_create_book_minimal_input(client, log: logging.Logger):
    """CreateBook accepts a title-only input with null genre/author."""
    step(log, "POST /graphql mutation createBook(title: Solo)")
    response = await client.post(
        "/graphql",
        json={"query": "mutation { createBook(input: {title: \"Solo\"}) "
                          "{ id title genre author } }"},
    )
    created = response.json()["data"]["createBook"]
    verify(log, "status code", response.status_code, 200)
    verify(log, "created title", created["title"], "Solo")
    verify(log, "created genre", created["genre"], None)
    verify(log, "created author", created["author"], None)


async def test_create_book_missing_title_is_validation_error(client, log: logging.Logger):
    """CreateBook without a title is rejected as a validation error."""
    step(log, "POST /graphql mutation createBook(genre: POETRY) -> expect error")
    response = await client.post(
        "/graphql",
        json={"query": "mutation { createBook(input: {genre: POETRY}) "
                          "{ id } }"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 400)
    verify_false(log, "data absent", "data" in payload)
    verify_true(
        log,
        "error mentions title",
        "title" in payload["errors"][0]["message"],
    )


async def test_delete_then_book_missing(client, log: logging.Logger):
    """A deleted book is no longer readable."""
    step(log, "POST /graphql mutation deleteBook(1)")
    deleted = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 1) }"},
    )
    verify(log, "delete response", deleted.json(), {"data": {"deleteBook": True}})
    step(log, "POST /graphql { book(id: 1) } -> expect error")
    read = await client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id } }"},
    )
    payload = read.json()
    verify(log, "status code", read.status_code, 400)
    verify(log, "data", payload["data"], None)
    verify(log, "error path", payload["errors"][0]["path"], ["book"])


async def test_book_query_nullable_fields(large_client, log: logging.Logger):
    """Book query surfaces null genre/author for a bare book."""
    step(log, "POST /graphql { book(id: 1) } on large dataset (bare book)")
    response = await large_client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id title genre author } }"},
    )
    book = response.json()["data"]["book"]
    verify(log, "status code", response.status_code, 200)
    verify(log, "book id", book["id"], 1)
    verify(log, "book genre", book["genre"], None)
    verify(log, "book author", book["author"], None)


async def test_books_genre_filter_no_matches(client, log: logging.Logger):
    """Books query with an empty genre filter returns no items."""
    step(log, "POST /graphql { books(genre: NONFICTION) } -> expect empty")
    response = await client.post(
        "/graphql",
        json={"query": "{ books(genre: NONFICTION) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    verify(log, "status code", response.status_code, 200)
    verify(log, "items", payload["items"], [])
    verify(log, "total", payload["total"], 0)


async def test_books_pagination_first_page(large_client, log: logging.Logger):
    """Books query page 1 returns the first 10 of 14 books."""
    step(log, "POST /graphql { books(page: 1) } on large dataset")
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 1) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    verify(log, "first page ids", [item["id"] for item in payload["items"]], list(range(1, 11)))
    verify(log, "total", payload["total"], 14)


async def test_books_pagination_second_page(large_client, log: logging.Logger):
    """Books query page 2 returns the remaining 4 of 14 books."""
    step(log, "POST /graphql { books(page: 2) } on large dataset")
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 2) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    verify(log, "second page ids", [item["id"] for item in payload["items"]], [11, 12, 13, 14])
    verify(log, "total", payload["total"], 14)


async def test_books_pagination_beyond_range(large_client, log: logging.Logger):
    """Books query beyond the last page returns no items."""
    step(log, "POST /graphql { books(page: 3) } on large dataset -> expect empty")
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 3) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    verify(log, "items", payload["items"], [])
    verify(log, "total", payload["total"], 14)


async def test_invalid_query_syntax(client, log: logging.Logger):
    """A syntactically invalid query is rejected with a parse error."""
    step(log, "POST /graphql '{ health {' -> expect parse error")
    response = await client.post(
        "/graphql",
        json={"query": "{ health {"},
    )
    payload = response.json()
    verify(log, "status code", response.status_code, 400)
    verify_false(log, "data absent", "data" in payload)
    verify_true(log, "error message present", bool(payload["errors"][0]["message"]))
