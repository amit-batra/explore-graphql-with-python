from ariadne import MutationType

from graphql import GraphQLError

from ..repositories import BookNotFoundError
from ..services import BookService

mutation = MutationType()


@mutation.field("createBook")
async def resolve_create_book(
    _parent,
    info,
    input: dict,
) -> object:
    service: BookService = info.context["book_service"]
    genre = input.get("genre")
    return await service.create_book(
        title=input["title"],
        genre=genre,
        author=input.get("author"),
    )


@mutation.field("deleteBook")
async def resolve_delete_book(_parent, info, id: int) -> bool:
    service: BookService = info.context["book_service"]
    try:
        return await service.delete_book(id)
    except BookNotFoundError:
        raise GraphQLError(
            f"Book with id {id} not found",
            extensions={"code": "NOT_FOUND"},
        ) from None
