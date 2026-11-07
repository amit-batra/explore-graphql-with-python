from __future__ import annotations

from .config import Settings


def main() -> None:
    import uvicorn

    settings = Settings()
    uvicorn.run(
        "explore_graphql_with_python.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
    )
