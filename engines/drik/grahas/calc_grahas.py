# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, datetime, timedelta, timezone
from typing import Dict

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.drik.core.noaa_sunrise import SunEvent, sunrise_local
from bheshajpatro.engines.drik.core import moshier_ephem  # noqa: F401
from bheshajpatro.engines.drik.core.ephemeris import calc_graha

__all__ = ["GRAHAS", "DailyGrahas", "daily_grahas"]


GRAHAS = (
    "surya",
    "chandra",
    "mangal",
    "budha",
    "guru",
    "shukra",
    "shani",
    "rahu",
    "ketu",
)


@dataclass(frozen=True)
class DailyGrahas:
    """
    Daily graha data for a given date and location.
    Sunrise is the primary Panchanga anchor.
    """
    date: _date
    latitude: float
    longitude: float
    std_meridian: float
    sunrise: SunEvent
    jd_ut_sunrise: float
    suryodaya_spashta: Dict[str, float]
    suryodaya_gati: Dict[str, float]


def _std_timezone(std_meridian: float) -> timezone:
    return timezone(timedelta(hours=std_meridian / 15.0))


def _utc_julian_day(dt_utc: datetime) -> float:
    """Swiss-free Julian Day calculation (Gregorian calendar)."""
    if dt_utc.tzinfo is None:
        raise ValueError("dt_utc must be timezone-aware")

    dt_utc = dt_utc.astimezone(timezone.utc)

    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day
    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )

    if m <= 2:
        y -= 1
        m += 12

    a = y // 100
    b = 2 - a + (a // 4)

    jd0 = (
        int(365.25 * (y + 4716))
        + int(30.6001 * (m + 1))
        + d + b - 1524.5
    )
    return jd0 + hour / 24.0


def daily_grahas(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    elevation: float | None = 0.0,
    use_topocentric: bool = True,
) -> DailyGrahas:
    """Compute daily graha positions anchored at local sunrise."""

    sunrise = sunrise_local(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
    )

    jd_ut_sunrise = _utc_julian_day(sunrise.event_utc)

    suryodaya_spashta: Dict[str, float] = {}
    suryodaya_gati: Dict[str, float] = {}

    lat_topo = latitude if use_topocentric else None
    lon_topo = longitude if use_topocentric else None

    for graha_name in GRAHAS:
        lonsr, _latsr, _distsr, lon_spdsr, _lat_spdsr, _dist_spdsr = calc_graha(
            graha_name,
            jd_ut_sunrise,
            latitude=lat_topo,
            longitude=lon_topo,
            elevation=elevation,
        )
        suryodaya_spashta[graha_name] = float(norm_360(lonsr))
        suryodaya_gati[graha_name] = float(lon_spdsr)

    return DailyGrahas(
        date=d,
        latitude=float(latitude),
        longitude=float(longitude),
        std_meridian=float(std_meridian),
        sunrise=sunrise,
        jd_ut_sunrise=jd_ut_sunrise,
        suryodaya_spashta=suryodaya_spashta,
        suryodaya_gati=suryodaya_gati,
    )