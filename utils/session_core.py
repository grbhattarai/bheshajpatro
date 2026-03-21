# bheshajpatro/utils/session_core.py

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bheshajpatro.utils.datatypes import SessionDict, PlaceDict


def get_date(session: SessionDict) -> date:
    """
    Return the session date as a Python date object.

    Accepts a stored value that may be a date, datetime, or ISO string.
    """
    d = session["context"]["date"]

    # Already a date (but not a datetime)
    if isinstance(d, date) and not isinstance(d, datetime):
        return d

    # Datetime -> date()
    if isinstance(d, datetime):
        return d.date()

    # Fallback: parse ISO-like string
    return date.fromisoformat(str(d))

def get_method(session: SessionDict) -> str:
    return str(
        session["context"].get("engine", session["context"].get("method", "ketaki"))
    ).lower()


def get_mode(session: SessionDict) -> str:
    """Return mode: 'grahas' or 'dmonthly' (default 'grahas')."""
    return str(session["context"].get("mode", "grahas")).lower()


def get_place(session: SessionDict) -> tuple[float, float, float, str | None]:
    """
    Extract place info as floats.

    Returns:
        (latitude, longitude, standard_meridian, timezone_string_or_None)
    """
    place: PlaceDict = session["context"]["place"]

    lat = float(place["latitude"])
    lon = float(place["longitude"])
    std = float(place["standard"])
    tz = place.get("tz")  # kept as Optional[str] for safety

    return lat, lon, std, tz
