from ariadne import QueryType

from ..models import Genre
from ..services import BookService, get_health

query = QueryType()


@query.field("health")
def resolve_health(_parent, _info) -> dict:
    return get_health()


@query.field("books")
async def resolve_books(
    _parent,
    info,
    genre: Genre | None = None,
    page: int = 1,
) -> dict:
    service: BookService = info.context["book_service"]
    page_result = await service.list_books(genre, page)
    return {
        "items": page_result.items,
        "total": page_result.total,
    }


@query.field("book")
async def resolve_book(_parent, info, id: int) -> object:
    service: BookService = info.context["book_service"]
    return await service.get_book(id)
