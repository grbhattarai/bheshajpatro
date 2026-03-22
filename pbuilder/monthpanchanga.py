# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Engine-agnostic monthly Panchanga builder.
#
# Accepts a daily engine runner, iterates over all days in the month,
# runs daypanchanga on each session, and returns a list of result rows.

from __future__ import annotations

from datetime import date as _date, timedelta
from typing import Any, Callable, Dict, List

from bheshajpatro.pbuilder.daypanchanga import run as panchanga_day_run

__all__ = [
    "month_boundaries",
    "build_month_panchanga_from_daily",
]


def month_boundaries(d: _date) -> tuple[_date, _date]:
    """Return (first_day, last_day) of the civil month for the given date."""
    first = _date(d.year, d.month, 1)
    if d.month == 12:
        next_first = _date(d.year + 1, 1, 1)
    else:
        next_first = _date(d.year, d.month + 1, 1)
    last = next_first - timedelta(days=1)
    return first, last


def _iter_month_days(d: _date):
    start, end = month_boundaries(d)
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def build_month_panchanga_from_daily(
    d: _date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float | None,
    daily_engine_run: Callable[..., Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Engine-agnostic monthly Panchanga builder.

    daily_engine_run must implement:
        run(d, latitude, longitude, std_meridian, tz_name, elevation) -> dict

    Returns a list of panchanga_result dicts, one per day of the month.
    """
    rows: List[Dict[str, Any]] = []

    for day in _iter_month_days(d):
        session = daily_engine_run(
            day,
            latitude_deg,
            longitude_deg,
            standard_meridian_deg,
            tz_name,
            elevation_m,
        )

        session = panchanga_day_run(session)

        result = session["astro"]["panchanga_result"].copy()
        result.setdefault("date_ce", day.isoformat())
        rows.append(result)

    return rows