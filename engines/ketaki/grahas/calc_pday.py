# bheshajpatro/ketaki/grahas/calc_pday.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date as _date
from typing import Any

from bheshajpatro.engines.ketaki.grahas.calc_grahas import (
    compute_daily_grahas_ketaki,
)
from bheshajpatro.engines.ketaki.core.anglefunc.ahargana import (
    compute_ahargana,
)


def _local_time_to_hours(dt) -> float:
    return (
        dt.hour
        + dt.minute / 60.0
        + dt.second / 3600.0
        + dt.microsecond / 3_600_000_000.0
    )


def build_session_from_ketaki(
    d: _date,
    *,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
) -> dict[str, Any]:
    """
    build a ketaki-style astro session for one date/place.

    mirrors drik dpanchanga_day structure so pbuilder can treat both engines
    uniformly.
    """
    daily = compute_daily_grahas_ketaki(
        d,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
    )

    sunrise_hours = _local_time_to_hours(daily.sunrise_local)
    sunset_hours = _local_time_to_hours(daily.sunset_local)

    ahargana_place = {
        "city": None,
        "latitude": float(latitude_deg),
        "longitude": float(longitude_deg),
        "std_meridian": float(standard_meridian_deg),
        "tz": tz_name,
    }
    aha = compute_ahargana(place=ahargana_place, for_date=d)

    session: dict[str, Any] = {
        "context": {
            "date": d.isoformat(),
            "location": {
                "latitude_deg": float(latitude_deg),
                "longitude_deg": float(longitude_deg),
                "standard_meridian_deg": float(standard_meridian_deg),
                "tz_name": tz_name,
            },
            "engine": "ketaki",
            "weekday_index": aha["weekday_index"],
            "weekday_name": aha["weekday_name"],
        },
        "astro": {
            "graha_spashta": daily.graha_spashta,
            "suryodayaspashta": daily.suryodayaspashta,
            "graha_gati": daily.graha_gati,
            "sunrise_hours": sunrise_hours,
            "sunset_hours": sunset_hours,
            "sunrise_local": daily.sunrise_local.isoformat(),
            "sunset_local": daily.sunset_local.isoformat(),
        },
        "ketaki": {
            "ahargana": aha,
        },
    }

    return session


def run(
    d: _date,
    *,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None = None,
    elevation_m: float | None = 0.0,
    ephe_dir: str | None = None,
) -> dict[str, Any]:
    """
    public entrypoint used by session_orchestrator and monthly builder.

    signature mirrors drik.grahas.dpanchanga_day.run; elevation_m and ephe_dir
    are ignored for ketaki.
    """
    _ = elevation_m, ephe_dir  # kept only for signature compatibility

    return build_session_from_ketaki(
        d=d,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
        tz_name=tz_name,
    )
