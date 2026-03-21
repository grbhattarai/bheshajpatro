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

# ----------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------

DAYS_PER_YEAR = 365.0
MINUTES_PER_DAY = 1440.0
SECONDS_PER_DAY = 24 * 60 * 60

# Standard solar zenith for sunrise/sunset (including refraction)
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
    """Return fractional year in radians (Meeus/NOAA convention)."""
    return 2.0 * pi / DAYS_PER_YEAR * (day_of_year - 1 + (hour - 12.0) / 24.0)


def _equation_of_time_and_declination(day_of_year: int) -> Tuple[float, float]:
    """
    Return (equation_of_time_minutes, declination_radians).

    equation_of_time_minutes:
        difference between apparent solar time and mean solar time (minutes).

    declination_radians:
        solar declination in radians.
    """
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
    """
    Sunrise or sunset time in minutes from midnight UTC (0–1440).

    Parameters
    ----------
    day_of_year : int
        Day of year (1–365/366).
    latitude, longitude : float
        Geographic coordinates in degrees.
    event : {"sunrise", "sunset"}
        Which event to compute.
    """
    eq_time, decl = _equation_of_time_and_declination(day_of_year)
    lat_rad = radians(float(latitude))

    cos_ha = (
        cos(radians(SUNRISE_SUNSET_ZENITH_DEG)) / (cos(lat_rad) * cos(decl))
        - tan(lat_rad) * tan(decl)
    )
    # Clamp for safety against numeric drift
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
    """
    Convert UTC datetime to local standard time using the given meridian.

    std_meridian:
        Standard time meridian in degrees (e.g., 86.25 for UTC+5:45).
    """
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


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.engines.drik.core.noaa_sunrise)
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running noaa_sunrise self-tests...")

    from datetime import date as _d

    # 1) Equator on (approx) March equinox: sunrise ~06:00, sunset ~18:00 UTC
    d_eq = _d(2025, 3, 20)
    eq_lat, eq_lon = 0.0, 0.0

    su_eq = sunrise_utc(d_eq, eq_lat, eq_lon)
    ss_eq = sunset_utc(d_eq, eq_lat, eq_lon)

    print("\n[ Equator, near March equinox, UTC ]")
    print("sunrise_utc:", su_eq)
    print("sunset_utc :", ss_eq)

    assert su_eq.tzinfo is timezone.utc
    assert ss_eq.tzinfo is timezone.utc
    assert su_eq < ss_eq

    # Rough sanity: sunrise between 4–8 UTC, sunset between 16–20 UTC
    assert 4 <= su_eq.hour <= 8
    assert 16 <= ss_eq.hour <= 20

    # 2) Kathmandu sample (27.7172N, 85.3240E, std meridian 86.25° → UTC+5.75)
    d_ktm = _d(2025, 1, 1)
    ktm_lat, ktm_lon, ktm_std_meridian = 27.7172, 85.3240, 86.25

    su_ktm = sunrise_local(d_ktm, ktm_lat, ktm_lon, ktm_std_meridian)
    ss_ktm = sunset_local(d_ktm, ktm_lat, ktm_lon, ktm_std_meridian)

    print("\n[ Kathmandu, local std time ]")
    print("sunrise_local:", su_ktm.event_local)
    print("sunset_local :", ss_ktm.event_local)

    # Basic sanity: local times exist and are ordered correctly
    assert su_ktm.event_local.tzinfo is not None
    assert ss_ktm.event_local.tzinfo is not None
    assert su_ktm.event_local < ss_ktm.event_local

    # Rough ranges for winter day in mid-latitude (Kathmandu):
    # sunrise between 5–8, sunset between 16–19 local.
    assert 5 <= su_ktm.event_local.hour <= 8
    assert 16 <= ss_ktm.event_local.hour <= 19

    print("\nAll noaa_sunrise self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()
