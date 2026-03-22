# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Calculate monthly Panchanga from daily loop for month boundaries.

from __future__ import annotations

from datetime import date as _date, timedelta
from typing import Any, Dict, List

from bheshajpatro.engines.drik.grahas.calc_pday import run as day_run

__all__ = ["month_bounds", "month_rows", "run"]


def month_bounds(d: _date) -> tuple[_date, _date]:
    """Return (first_day_of_month, last_day_of_month) for the given date."""
    first = _date(d.year, d.month, 1)
    if d.month == 12:
        next_first = _date(d.year + 1, 1, 1)
    else:
        next_first = _date(d.year, d.month + 1, 1)
    last = next_first - timedelta(days=1)
    return first, last


def _iter_month_days(d: _date):
    start, end = month_bounds(d)
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def month_rows(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None = None,
    elevation: float | None = 0.0,
) -> List[Dict[str, Any]]:
    """
    Build a list of per-day rows for the month containing date d.

    Each row:
        {
            "date":    ISO string,
            "year":    int,
            "month":   int,
            "day":     int,
            "session": full daily session from calc_pday.run,
        }
    """
    rows: List[Dict[str, Any]] = []

    for day in _iter_month_days(d):
        session = day_run(
            day,
            latitude=latitude,
            longitude=longitude,
            std_meridian=std_meridian,
            tz_name=tz_name,
            elevation=elevation,
        )
        rows.append({
            "date":    day.isoformat(),
            "year":    day.year,
            "month":   day.month,
            "day":     day.day,
            "session": session,
        })

    return rows


def run(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None = None,
    elevation: float | None = 0.0,
) -> List[Dict[str, Any]]:
    """Public entry point for monthly aggregation."""
    return month_rows(
        d=d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        tz_name=tz_name,
        elevation=elevation,
    )