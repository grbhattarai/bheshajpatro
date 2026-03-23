# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date as _date, timedelta
from typing import Any, Iterator

from bheshajpatro.engines.ketaki.grahas.calc_pday import run as ketaki_day_run

__all__ = [
    "month_boundaries",
    "build_month_rows",
    "run",
    "format_month_table",
]


def month_boundaries(d: _date) -> tuple[_date, _date]:
    first = _date(d.year, d.month, 1)
    if d.month == 12:
        next_first = _date(d.year + 1, 1, 1)
    else:
        next_first = _date(d.year, d.month + 1, 1)

    last = next_first - timedelta(days=1)
    return first, last


def _iter_month_days(d: _date) -> Iterator[_date]:
    start, end = month_boundaries(d)
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def build_month_rows(
    d: _date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None = None,
    elevation_m: float | None = 0.0,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for day in _iter_month_days(d):
        session = ketaki_day_run(
            day,
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            standard_meridian_deg=standard_meridian_deg,
            tz_name=tz_name,
            elevation_m=elevation_m,
        )

        astro = session["astro"]

        rows.append(
            {
                "date": day.isoformat(),
                "year": day.year,
                "month": day.month,
                "day": day.day,
                "sunrise_hours": float(astro["sunrise_hours"]),
                "sunset_hours": float(astro["sunset_hours"]),
                "surya_gati": float(astro["graha_gati"]["surya"]),
                "surya_spashta": float(astro["suryodayaspashta"]["surya"]),
                "chandra_gati": float(astro["graha_gati"]["chandra"]),
                "chandra_spashta": float(astro["suryodayaspashta"]["chandra"]),
            }
        )

    return rows


def run(
    d: _date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None = None,
    elevation_m: float | None = 0.0,
) -> list[dict[str, Any]]:
    return build_month_rows(
        d=d,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
        tz_name=tz_name,
        elevation_m=elevation_m,
    )


def format_month_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no data)"

    lines: list[str] = []
    lines.append(
        "Month      Day  Sunrise Sunset SuryaGati SuryaSpashta "
        "ChandraGati ChandraSpashta"
    )
    lines.append("-" * 90)

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    for r in rows:
        mname = month_names[r["month"] - 1]

        sunrise = (
            f"{int(r['sunrise_hours']):02d}:"
            f"{int((r['sunrise_hours'] % 1) * 60):02d}"
        )
        sunset = (
            f"{int(r['sunset_hours']):02d}:"
            f"{int((r['sunset_hours'] % 1) * 60):02d}"
        )

        lines.append(
            f"{mname:<10} {r['day']:>3}  "
            f"{sunrise:>6}  {sunset:>6}  "
            f"{r['surya_gati']:.3f}      {r['surya_spashta']:.3f}      "
            f"{r['chandra_gati']:.3f}        {r['chandra_spashta']:.3f}"
        )

    return "\n".join(lines)