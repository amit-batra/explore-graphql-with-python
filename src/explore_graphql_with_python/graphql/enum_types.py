from ariadne import EnumType

from ..models import Genre

genre_type = EnumType("Genre", Genre)
