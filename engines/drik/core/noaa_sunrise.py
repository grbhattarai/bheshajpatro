# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Compact NOAA/Meeus sunrise/sunset (UTC + std local time).

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, datetime, timedelta, timezone
from math import acos, cos, radians, sin, tan, pi
from typing import Literal, Tuple

__all__ = [
    "SunEvent",
    "sunrise_utc",
    "sunset_utc",
    "sunrise_local",
    "sunset_local",
]

DAYS_PER_YEAR = 365.0
MINUTES_PER_DAY = 1440.0
SECONDS_PER_DAY = 24 * 60 * 60
SUNRISE_SUNSET_ZENITH_DEG = 90.833


@dataclass(frozen=True)
class SunEvent:
    """Sunrise/sunset for one date and location (standard time only)."""

    date: _date
    latitude: float
    longitude: float
    event_utc: datetime
    event_local: datetime  # std time, no DST


def _fraction_of_year(day_of_year: int, hour: float = 0.0) -> float:
    return 2.0 * pi / DAYS_PER_YEAR * (day_of_year - 1 + (hour - 12.0) / 24.0)


def _equation_of_time_and_declination(day_of_year: int) -> Tuple[float, float]:
    frac_year = _fraction_of_year(day_of_year, hour=0.0)

    eq_time = 229.18 * (
        0.000075
        + 0.001868 * cos(frac_year)
        - 0.032077 * sin(frac_year)
        - 0.014615 * cos(2 * frac_year)
        - 0.040849 * sin(2 * frac_year)
    )

    decl = (
        0.006918
        - 0.399912 * cos(frac_year)
        + 0.070257 * sin(frac_year)
        - 0.006758 * cos(2 * frac_year)
        + 0.000907 * sin(2 * frac_year)
        - 0.002697 * cos(3 * frac_year)
        + 0.00148 * sin(3 * frac_year)
    )

    return eq_time, decl


def _event_minutes_utc(
    day_of_year: int,
    latitude: float,
    longitude: float,
    event: Literal["sunrise", "sunset"],
) -> float:
    eq_time, decl = _equation_of_time_and_declination(day_of_year)
    lat_rad = radians(float(latitude))

    cos_ha = (
        cos(radians(SUNRISE_SUNSET_ZENITH_DEG)) / (cos(lat_rad) * cos(decl))
        - tan(lat_rad) * tan(decl)
    )
    cos_ha = max(-1.0, min(1.0, cos_ha))
    ha_deg = acos(cos_ha) * 180.0 / pi

    if event == "sunrise":
        hour_angle = +ha_deg
    elif event == "sunset":
        hour_angle = -ha_deg
    else:
        raise ValueError("event must be 'sunrise' or 'sunset'")

    minutes = 720.0 - 4.0 * (longitude + hour_angle) - eq_time
    return minutes % MINUTES_PER_DAY


def _minutes_to_hms(minutes: float) -> Tuple[int, int, int]:
    total_seconds = int(round(minutes * 60.0)) % SECONDS_PER_DAY
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return h, m, s


def sunrise_utc(d: _date, latitude: float, longitude: float) -> datetime:
    """Return sunrise time (UTC) for a given date and location."""
    day_of_year = d.timetuple().tm_yday
    minutes = _event_minutes_utc(day_of_year, latitude, longitude, "sunrise")
    h, m, s = _minutes_to_hms(minutes)
    return datetime(d.year, d.month, d.day, h, m, s, tzinfo=timezone.utc)


def sunset_utc(d: _date, latitude: float, longitude: float) -> datetime:
    """Return sunset time (UTC) for a given date and location."""
    day_of_year = d.timetuple().tm_yday
    minutes = _event_minutes_utc(day_of_year, latitude, longitude, "sunset")
    h, m, s = _minutes_to_hms(minutes)
    return datetime(d.year, d.month, d.day, h, m, s, tzinfo=timezone.utc)


def _to_local_standard_time(event_utc: datetime, std_meridian: float) -> datetime:
    """Convert UTC datetime to local standard time using the given meridian."""
    offset_hours = std_meridian / 15.0
    tz = timezone(timedelta(hours=offset_hours))
    return event_utc.astimezone(tz)


def sunrise_local(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
) -> SunEvent:
    """Return sunrise as SunEvent (UTC + local standard time)."""
    event_utc = sunrise_utc(d, latitude, longitude)
    event_local = _to_local_standard_time(event_utc, std_meridian)
    return SunEvent(d, float(latitude), float(longitude), event_utc, event_local)


def sunset_local(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
) -> SunEvent:
    """Return sunset as SunEvent (UTC + local standard time)."""
    event_utc = sunset_utc(d, latitude, longitude)
    event_local = _to_local_standard_time(event_utc, std_meridian)
    return SunEvent(d, float(latitude), float(longitude), event_utc, event_local)
