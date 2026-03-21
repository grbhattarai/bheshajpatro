# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Engine-agnostic MONTHLY Panchanga builder.
#
# You pass in a daily engine runner (e.g. Drik calc_pday.run),
# and this module:
#   1) calls the engine for each civil day of the month
#   2) runs daypanchanga.run() on the session
#   3) collects session["astro"]["panchanga_result"] rows

from __future__ import annotations

# =============================================================================
# DEV OVERRIDE (REMOVE AFTER TESTING)
# -----------------------------------------------------------------------------
# Allows direct execution:
#     python pbuilder/pa3_monthpanchanga.py
# =============================================================================
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    PACKAGE_PARENT = Path(__file__).resolve().parents[2]
    if str(PACKAGE_PARENT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_PARENT))
# =============================================================================

from datetime import date as _date, timedelta
from typing import Any, Callable, Dict, List

from bheshajpatro.pbuilder.daypanchanga import run as panchanga_day_run

__all__ = [
    "month_boundaries",
    "build_month_panchanga_from_daily",
    "format_month_table",
]


# ---------------------------------------------------------------------------
# Month utilities
# ---------------------------------------------------------------------------

def month_boundaries(d: _date) -> tuple[_date, _date]:
    """
    Given a date, return (first_day, last_day) of that civil month.
    """
    first = _date(d.year, d.month, 1)
    if d.month == 12:
        next_first = _date(d.year + 1, 1, 1)
    else:
        next_first = _date(d.year, d.month + 1, 1)
    last = next_first - timedelta(days=1)
    return first, last


def _iter_month_days(d: _date):
    """
    Yield all dates in the civil month of the given date.
    """
    start, end = month_boundaries(d)
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


# ---------------------------------------------------------------------------
# Core: engine-agnostic MONTHLY Panchanga
# ---------------------------------------------------------------------------

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
    Engine-agnostic MONTHLY Panchanga builder.

    daily_engine_run must implement something equivalent to:

        run(
            d: date,
            latitude: float,
            longitude: float,
            std_meridian: float,
            tz_name: str | None = None,
            elevation: float | None = 0.0,
        ) -> dict[str, Any]

    The returned dict must be an engine session compatible with
    pbuilder.daypanchanga.run(session).
    """
    rows: List[Dict[str, Any]] = []

    for day in _iter_month_days(d):
        # 1) engine daily session
        session = daily_engine_run(
            day,
            latitude_deg,
            longitude_deg,
            standard_meridian_deg,
            tz_name,
            elevation_m,
        )

        # 2) Panchanga builder
        session = panchanga_day_run(session)

        result = session["astro"]["panchanga_result"].copy()
        result.setdefault("date_ce", day.isoformat())
        rows.append(result)

    return rows


# ---------------------------------------------------------------------------
# Pretty text table (optional helper)
# ---------------------------------------------------------------------------

def format_month_table(rows: List[Dict[str, Any]]) -> str:
    """
    Make a simple human-readable ASCII table from monthly Panchanga rows.

    Rows are days (1..31), columns are key Panchanga values.
    """
    if not rows:
        return "(no data)"

    headers = [
        "Date",
        "Day",
        "Tithi1",
        "Tithi1Name",
        "Naksh1",
        "Naksh1Name",
        "Yoga1",
        "Yoga1Name",
        "Sunrise",
        "Sunset",
    ]

    table_rows: List[str] = []

    table_rows.append(
        "{:<10} {:<9} {:>5} {:<16} {:>5} {:<16} {:>5} {:<16} {:>8} {:>8}".format(
            *headers
        )
    )
    table_rows.append("-" * 110)

    for r in rows:
        date_ce = r.get("date_ce", "")
        day_name = r.get("day_name", "")

        tithi1 = r.get("tithi1", "")
        tithi1_name = r.get("tithi1_name", "")

        naks1 = r.get("nakshatra1", "")
        naks1_name = r.get("nakshatra1_name", "")

        yoga1 = r.get("yoga1", "")
        yoga1_name = r.get("yoga1_name", "")

        sunrise = r.get("sunrise_hm", "")
        sunset = r.get("sunset_hm", "")

        line = "{:<10} {:<9} {:>5} {:<16} {:>5} {:<16} {:>5} {:<16} {:>8} {:>8}".format(
            date_ce,
            day_name,
            tithi1,
            tithi1_name,
            naks1,
            naks1_name,
            yoga1,
            yoga1_name,
            sunrise,
            sunset,
        )
        table_rows.append(line)

    return "\n".join(table_rows)


# ---------------------------------------------------------------------------
# SIMPLE SELF-TESTS
# ---------------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running pa3_monthpanchanga self-tests...")

    from datetime import date as _d
    from bheshajpatro.engines.drik.grahas.calc_pday import run as drik_day_run

    d_test = _d(2025, 1, 15)

    rows = build_month_panchanga_from_daily(
        d=d_test,
        latitude_deg=27.7172,
        longitude_deg=85.3240,
        standard_meridian_deg=86.25,
        tz_name="Asia/Kathmandu",
        elevation_m=1300.0,
        daily_engine_run=drik_day_run,
    )

    print(f"\nMonth rows count: {len(rows)}")
    assert len(rows) == 31

    first = rows[0]
    print("\nFirst row keys:", list(first.keys()))
    print("First row date:", first.get("date_ce"))
    print("First row day :", first.get("day_name"))
    print("First row tithi:", first.get("tithi1"), first.get("tithi1_name"))
    print("First row naksh:", first.get("nakshatra1"), first.get("nakshatra1_name"))
    print("First row yoga :", first.get("yoga1"), first.get("yoga1_name"))

    for row in rows:
        assert "date_ce" in row
        assert "day_name" in row
        assert "tithi1" in row
        assert "nakshatra1" in row
        assert "yoga1" in row
        assert "sunrise_hm" in row
        assert "sunset_hm" in row

    print("\n--- Month Table Preview ---")
    print(format_month_table(rows[:5]))

    print("\nAll monthpanchanga self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()