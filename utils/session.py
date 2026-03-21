# bheshajpatro/utils/session.py

"""
Legacy session helpers — now reduced to minimal stubs.

Your new system (Drik-first) does not use the old SessionDict system.
We only keep small extractors for compatibility where needed.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Basic extractors (kept because some old code uses them)
# ---------------------------------------------------------------------------

def get_date(session: Dict[str, Any]) -> date:
    d = session["context"]["date"]
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    return date.fromisoformat(str(d))


def get_method(session: Dict[str, Any]) -> str:
    return session["context"].get("engine", "ketaki")


def get_mode(session: Dict[str, Any]) -> str:
    return "grahas"


def get_place(session: Dict[str, Any]) -> tuple[float, float, float, str | None]:
    place = session["context"]["place"]
    lat = float(place["latitude"])
    lon = float(place["longitude"])
    std = float(place.get("standard", 0))
    tz = place.get("tz")
    return lat, lon, std, tz


# ---------------------------------------------------------------------------
# Stub to satisfy imports
# ---------------------------------------------------------------------------

def ensure_monthly_cache(*args, **kwargs):
    """No-op stub preserved for backwards compatibility."""
    return None
