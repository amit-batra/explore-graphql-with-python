from __future__ import annotations

from typing import Any

from fastapi import Request


async def get_context_value(request: Request, data: Any) -> dict[str, Any]:
    return {
        "request": request,
        "book_service": request.app.state.book_service,
    }
