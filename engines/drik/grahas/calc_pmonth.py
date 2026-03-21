# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

# Calculate monthly from daily loop for month boundaries

from __future__ import annotations

from datetime import date as _date, timedelta
from typing import Any, Dict, List

from bheshajpatro.engines.drik.grahas.calc_pday import run as day_run

__all__ = ["month_bounds", "month_rows", "run", "format_month_table"]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


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
    ephe_dir: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Build a list of per-day rows for the month containing date d.

    Each row has:
        {
            "date": ISO string for the day,
            "year": int,
            "month": int,
            "day": int,
            "session": <full daily session from calc_pday.run>,
        }

    We do NOT cherry-pick any astro fields here. Whatever calc_pday.run
    provides (tithi, nakshatra, yoga, karanas, sunrise, sunset, etc.)
    will all be available under row["session"].
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
            ephe_dir=ephe_dir,
        )

        rows.append(
            {
                "date": day.isoformat(),
                "year": day.year,
                "month": day.month,
                "day": day.day,
                "session": session,  # full daily session (context + astro)
            }
        )

    return rows


def run(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None = None,
    elevation: float | None = 0.0,
    ephe_dir: str | None = None,
) -> List[Dict[str, Any]]:
    """Public entry point for monthly aggregation."""
    return month_rows(
        d=d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        tz_name=tz_name,
        elevation=elevation,
        ephe_dir=ephe_dir,
    )


def format_month_table(rows: List[Dict[str, Any]]) -> str:
    """
    Render a simple text table from monthly rows (diagnostic only).

    For now, this uses a few fields from the daily session for preview.
    This is *not* meant for final UI; just a quick console view.
    """
    if not rows:
        return "(no data)"

    lines: List[str] = []
    lines.append(
        "Month      Day  Sunrise Sunset SuryaGati SuryaSpashta ChandraGati ChandraSpashta"
    )
    lines.append("-" * 90)

    for r in rows:
        mname = MONTH_NAMES[r["month"] - 1]
        day = r["day"]
        session = r["session"]
        astro = session["astro"]

        # These are just for preview; the monthly/UI layer can use
        # any other fields from session["astro"] later.
        sunrise_hours = astro.get("sunrise_hours")
        sunset_hours = astro.get("sunset_hours")
        graha_gati = astro.get("graha_gati", {})
        suryodaya_spashta = astro.get("suryodaya_spashta", {})

        # Fallbacks in case something is missing
        sr_h = float(sunrise_hours) if sunrise_hours is not None else 0.0
        ss_h = float(sunset_hours) if sunset_hours is not None else 0.0

        sunrise = f"{int(sr_h):02d}:{int((sr_h % 1) * 60):02d}"
        sunset = f"{int(ss_h):02d}:{int((ss_h % 1) * 60):02d}"

        surya_gati = float(graha_gati.get("surya", 0.0))
        surya_spashta = float(suryodaya_spashta.get("surya", 0.0))
        chandra_gati = float(graha_gati.get("chandra", 0.0))
        chandra_spashta = float(suryodaya_spashta.get("chandra", 0.0))

        lines.append(
            f"{mname:<10} {day:>3}  "
            f"{sunrise:>6}  {sunset:>6}  "
            f"{surya_gati:.3f}      {surya_spashta:.3f}      "
            f"{chandra_gati:.3f}        {chandra_spashta:.3f}"
        )

    return "\n".join(lines)


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.engines.drik.grahas.calc_pmonth)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.engines.drik.grahas.calc_pmonth)
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running calc_pmonth self-tests...")

    from datetime import date as _d

    d_test = _d(2025, 1, 15)  # mid-month, January 2025
    lat_ktm = 27.7172
    lon_ktm = 85.3240
    std_meridian_ktm = 86.25

    rows = run(
        d_test,
        latitude=lat_ktm,
        longitude=lon_ktm,
        std_meridian=std_meridian_ktm,
        tz_name="Asia/Kathmandu",
        elevation=1300.0,
        ephe_dir=None,
    )

    # Basic month length sanity
    print(f"\nMonth rows count: {len(rows)}")
    assert len(rows) in (28, 29, 30, 31)

    # Check a few generic structural properties on all rows
    for idx, r in enumerate(rows):
        assert "date" in r
        assert "year" in r
        assert "month" in r
        assert "day" in r
        assert "session" in r

        session = r["session"]
        assert isinstance(session, dict), "session must be a dict"
        assert "context" in session, "session missing 'context'"
        assert "astro" in session, "session missing 'astro'"

        context = session["context"]
        astro = session["astro"]
        assert isinstance(context, dict), "context must be a dict"
        assert isinstance(astro, dict), "astro must be a dict"

        # Generic consistency: context.date should match row.date, if present
        ctx_date = context.get("date")
        if ctx_date is not None:
            assert ctx_date == r["date"], (
                f"context.date ({ctx_date}) != row.date ({r['date']}) "
                f"at index {idx}"
            )

    # Print a small preview for visual inspection
    # Log preview
    first = rows[0]
    print("\nFirst row keys:", list(first.keys()))
    print("First row date:", first["date"])
    print("First row session.context keys:", list(first["session"]["context"].keys()))
    print("First row session.astro keys  :", list(first["session"]["astro"].keys()))

    # Generic astro preview
    print("\n--- Astro Values (First Row) ---")
    astro = first["session"]["astro"]
    for key, value in astro.items():
        if isinstance(value, float):
            print(f"{key:20}: {value:.6f}")
        elif isinstance(value, dict):
            print(f"{key:20}:")
            for k2, v2 in value.items():
                print(f"    {k2:12} -> {v2}")
        else:
            print(f"{key:20}: {value}")

    print("\nAll calc_pmonth self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()
