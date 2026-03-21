from __future__ import annotations

from typing import Any, TypedDict


class PlaceDict(TypedDict):
    """
    Canonical place representation used in the backend.

    All keys are required; values come from worldcities.csv (or validated
    JSON), so they should always be present.
    """
    country: str
    state: str
    city: str
    latitude: float
    longitude: float
    standard: float
    tz: str


class SessionDict(TypedDict):
    """
    Top-level session object used throughout the bheshajpatro pipeline.
    """
    id: str
    schema_version: str
    created_utc: str
    context: dict[str, Any]
    engine: dict[str, Any]
    cache: dict[str, Any]
