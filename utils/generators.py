# bheshajpatro/utils/generators.py

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from bheshajpatro.pbuilder.service import get_panchanga_session


def generate_month(
    place: Dict[str, Any],
    year: int,
    month: int,
    engine: str = "drik",
) -> List[Dict[str, Any]]:
    """
    Generate Panchanga sessions for every day in a given month.

    Each element of the returned list is a 'session' dict in the same
    format as returned by get_panchanga_session(), which is a thin
    wrapper around your underlying engine build_session/build_session_drik.

    This replaces any older implementation that depended on a
    bheshajpatro.ketaki.run_daily() that does not exist yet.
    """
    sessions: List[Dict[str, Any]] = []

    # Start from the first of the month
    current = date(year, month, 1)

    # Loop until we leave the requested month
    while current.month == month:
        sess = get_panchanga_session(current, place, engine=engine)
        sessions.append(sess)
        current += timedelta(days=1)

    return sessions
