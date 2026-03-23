# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date as _date
from typing import Any

from bheshajpatro.engines.ketaki.grahas.calc_grahas import (
    compute_daily_grahas_ketaki,
)


def _local_time_to_hours(dt) -> float:
    return (
        dt.hour
        + dt.minute / 60.0
        + dt.second / 3600.0
        + dt.microsecond / 3_600_000_000.0
    )


def _python_weekday_to_display_id(py_weekday: int) -> int:
    # Python: 0=Mon ... 6=Sun
    # Display: 1=Sun ... 7=Sat
    return ((int(py_weekday) + 1) % 7) + 1


def _weekday_name_from_display_id(weekday_id: int) -> str:
    names = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday",
    }
    return names[int(weekday_id)]


def build_session_from_ketaki(
    d: _date,
    *,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
) -> dict[str, Any]:
    """
    Build one Ketaki raw engine session.

    This mirrors the raw session structure expected by registry /
    session_orchestrator / pbuilder.
    """
    daily = compute_daily_grahas_ketaki(
        d,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
    )

    sunrise_hours = _local_time_to_hours(daily.sunrise_local)
    sunset_hours = _local_time_to_hours(daily.sunset_local)

    weekday_id = _python_weekday_to_display_id(d.weekday())

    session: dict[str, Any] = {
        "context": {
            "date": d.isoformat(),
            "location": {
                "latitude": float(latitude_deg),
                "longitude": float(longitude_deg),
                "std_meridian": float(standard_meridian_deg),
                "tz_name": tz_name,
                "elevation": 0.0,
            },
            "engine": "ketaki",
            "weekday_id": weekday_id,
            "day_name": _weekday_name_from_display_id(weekday_id),
        },
        "astro": {
            # Keep internal full graha positions if useful elsewhere
            "graha_spashta": daily.graha_spashta,

            # These two names must match pbuilder/daypanchanga.py expectations
            "suryodaya_spashta": daily.suryodayaspashta,
            "suryodaya_gati": daily.graha_gati,

            "sunrise_hours": float(sunrise_hours),
            "sunset_hours": float(sunset_hours),
            "sunrise_local": daily.sunrise_local.isoformat(),
            "sunset_local": daily.sunset_local.isoformat(),
            "jd_6am_local": float(daily.jd_6am_local),
            "jd_sunrise_local": float(daily.jd_sunrise_local),
        },
    }

    return session


def run(
    d: _date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None = None,
    elevation_m: float | None = 0.0,
) -> dict[str, Any]:
    """
    Public Ketaki day entrypoint.

    Signature matches the way registry/session_orchestrator call engine runners.
    `elevation_m` is accepted for compatibility and ignored.
    """
    _ = elevation_m

    return build_session_from_ketaki(
        d=d,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
        tz_name=tz_name,
    )