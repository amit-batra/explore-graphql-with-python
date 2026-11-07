

async def test_health_query(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ health { status } }"},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"health": {"status": "OK"}}}


async def test_books_query(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ books { items { id title genre author } total } }"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["books"]["total"] == 2
    assert payload["data"]["books"]["items"][0]["title"] == "The Great Gatsby"
    assert payload["data"]["books"]["items"][1]["genre"] == "SCI_FI"


async def test_books_query_genre_filter(client):
    response = await client.post(
        "/graphql",
        json={
            "query": "{ books(genre: SCI_FI) { items { id title } total } }",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["books"]["total"] == 1
    assert payload["data"]["books"]["items"][0]["title"] == "Dune"


async def test_book_query(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id title genre author } }"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["book"]["title"] == "The Great Gatsby"


async def test_book_query_missing(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ book(id: 999) { id title } }"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["message"]


async def test_create_book_mutation(client):
    response = await client.post(
        "/graphql",
        json={
            "query": (
                "mutation { createBook(input: {title: \"New\", "
                "genre: POETRY, author: \"X\"}) { id title genre author } }"
            ),
        },
    )
    assert response.status_code == 200
    payload = response.json()
    created = payload["data"]["createBook"]
    assert created["title"] == "New"
    assert created["genre"] == "POETRY"
    assert created["id"] == 3


async def test_delete_book_mutation(client):
    response = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 1) }"},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"deleteBook": True}}


async def test_delete_book_missing_returns_not_found(client):
    response = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 999) }"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["extensions"]["code"] == "NOT_FOUND"


async def test_create_then_read(client):
    create = await client.post(
        "/graphql",
        json={
            "query": (
                "mutation { createBook(input: {title: \"Added\"}) "
                "{ id title } }"
            ),
        },
    )
    assert create.status_code == 200
    book_id = create.json()["data"]["createBook"]["id"]

    read = await client.post(
        "/graphql",
        json={"query": f"{{ book(id: {book_id}) {{ id title }} }}"},
    )
    assert read.status_code == 200
    assert read.json()["data"]["book"]["title"] == "Added"


async def test_create_book_minimal_input(client):
    response = await client.post(
        "/graphql",
        json={"query": "mutation { createBook(input: {title: \"Solo\"}) "
                          "{ id title genre author } }"},
    )
    assert response.status_code == 200
    created = response.json()["data"]["createBook"]
    assert created["title"] == "Solo"
    assert created["genre"] is None
    assert created["author"] is None


async def test_create_book_missing_title_is_validation_error(client):
    response = await client.post(
        "/graphql",
        json={"query": "mutation { createBook(input: {genre: POETRY}) "
                          "{ id } }"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert "data" not in payload
    assert "title" in payload["errors"][0]["message"]


async def test_delete_then_book_missing(client):
    deleted = await client.post(
        "/graphql",
        json={"query": "mutation { deleteBook(id: 1) }"},
    )
    assert deleted.json() == {"data": {"deleteBook": True}}

    read = await client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id } }"},
    )
    assert read.status_code == 400
    payload = read.json()
    assert payload["data"] is None
    assert payload["errors"][0]["path"] == ["book"]


async def test_book_query_nullable_fields(large_client):
    response = await large_client.post(
        "/graphql",
        json={"query": "{ book(id: 1) { id title genre author } }"},
    )
    assert response.status_code == 200
    book = response.json()["data"]["book"]
    assert book["id"] == 1
    assert book["genre"] is None
    assert book["author"] is None


async def test_books_genre_filter_no_matches(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ books(genre: NONFICTION) "
                          "{ items { id } total } }"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]["books"]
    assert payload["items"] == []
    assert payload["total"] == 0


async def test_books_pagination_first_page(large_client):
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 1) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    assert [item["id"] for item in payload["items"]] == list(range(1, 11))
    assert payload["total"] == 14


async def test_books_pagination_second_page(large_client):
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 2) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    assert [item["id"] for item in payload["items"]] == [11, 12, 13, 14]
    assert payload["total"] == 14


async def test_books_pagination_beyond_range(large_client):
    response = await large_client.post(
        "/graphql",
        json={"query": "{ books(page: 3) { items { id } total } }"},
    )
    payload = response.json()["data"]["books"]
    assert payload["items"] == []
    assert payload["total"] == 14


async def test_invalid_query_syntax(client):
    response = await client.post(
        "/graphql",
        json={"query": "{ health {"},
    )
    assert response.status_code == 400
    payload = response.json()
    assert "data" not in payload
    assert payload["errors"][0]["message"]
