from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HealthStatusResponse:
    status: str


def get_health() -> HealthStatusResponse:
    return HealthStatusResponse(status="OK")
