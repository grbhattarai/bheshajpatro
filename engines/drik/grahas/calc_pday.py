# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Build one-day Drik Panchanga session (engine-agnostic output shape)

from __future__ import annotations

from datetime import date as _date, datetime
from typing import Any, Dict

from bheshajpatro.engines.drik.core.noaa_sunrise import sunset_local
from bheshajpatro.engines.drik.grahas.calc_grahas import daily_grahas

__all__ = ["build_session", "run"]


def _local_hours(dt: datetime) -> float:
    """Convert a local datetime to fractional hours since local midnight."""
    return (
        dt.hour
        + dt.minute / 60.0
        + dt.second / 3600.0
        + dt.microsecond / 3_600_000_000.0
    )


def build_session(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None,
    elevation: float | None,
) -> Dict[str, Any]:
    """
    Engine-specific builder, engine-agnostic session output.
    Sunrise is the primary Panchanga anchor.
    """
    daily = daily_grahas(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        elevation=elevation,
        use_topocentric=True,
    )

    sunset_event = sunset_local(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
    )

    sunrise_hours = _local_hours(daily.sunrise.event_local)
    sunset_hours = _local_hours(sunset_event.event_local)

    return {
        "context": {
            "date": d.isoformat(),
            "location": {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "std_meridian": float(std_meridian),
                "tz_name": tz_name,
                "elevation": float(elevation or 0.0),
            },
            "engine": "drik",
        },
        "astro": {
            "suryodaya_spashta": daily.suryodaya_spashta,
            "suryodaya_gati": daily.suryodaya_gati,
            "sunrise_hours": sunrise_hours,
            "sunset_hours": sunset_hours,
            "sunrise_local": daily.sunrise.event_local.isoformat(),
            "sunset_local": sunset_event.event_local.isoformat(),
            "jd_ut_sunrise": daily.jd_ut_sunrise,
        },
    }


def run(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None = None,
    elevation: float | None = 0.0,
) -> Dict[str, Any]:
    """Public entry point for one-day Drik Panchanga session."""
    return build_session(
        d=d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        tz_name=tz_name,
        elevation=elevation,
    )