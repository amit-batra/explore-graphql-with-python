from pathlib import Path

from ariadne import load_schema_from_path, make_executable_schema

from .enum_types import genre_type
from .mutations import mutation
from .queries import query

BASE_DIR = Path(__file__).resolve().parents[3]
SDL_PATH = BASE_DIR / "schema"


def build_schema():
    type_defs = load_schema_from_path(SDL_PATH / "schema.graphql")
    return make_executable_schema(
        type_defs,
        query,
        mutation,
        genre_type,
    )
