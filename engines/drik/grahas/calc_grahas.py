# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Drik daily grahas: 06:00 + sunrise (nirayana + tropical speed).

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, datetime, timezone, timedelta
from typing import Dict

import swisseph as swe

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.drik.core.noaa_sunrise import sunrise_local, SunEvent
from bheshajpatro.engines.drik.core.swiss_ephem import calc_graha

__all__ = ["DailyGrahas", "daily_grahas"]

# Canonical list of grahas (Hindu names)
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

    All longitudes are nirayana (Lahiri sidereal), in degrees [0, 360).
    Speeds are tropical longitude speeds (deg/day) at 06:00 std local time.
    """

    date: _date
    latitude: float
    longitude: float
    std_meridian: float

    sunrise: SunEvent
    jd_ut_6: float          # Julian day at 06:00 (UT)
    jd_ut_sunrise: float    # Julian day at sunrise (UT)

    graha_spashta: Dict[str, float]       # nirayana at 06:00
    suryodaya_spashta: Dict[str, float]   # nirayana at sunrise
    graha_gati: Dict[str, float]          # tropical lon speed at 06:00


def _std_timezone(std_meridian: float) -> timezone:
    """
    Return a fixed-offset timezone from the standard meridian (deg).

    Example: std_meridian = 86.25 -> UTC+5:45.
    """
    offset_hours = std_meridian / 15.0
    return timezone(timedelta(hours=offset_hours))


def _utc_julian_day(dt_utc: datetime) -> float:
    """
    Convert a timezone-aware UTC datetime to Julian day (UT) using Swiss Ephemeris.
    """
    if dt_utc.tzinfo is None:
        raise ValueError("dt_utc must be timezone-aware")

    dt_utc = dt_utc.astimezone(timezone.utc)

    year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )
    return float(swe.julday(year, month, day, hour))


def daily_grahas(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    elevation: float | None = 0.0,
    ephe_dir: str | None = None,
    use_topocentric: bool = True,
) -> DailyGrahas:
    """
    Compute daily graha data (nirayana + tropical speed) at 06:00 and sunrise.

    Parameters
    ----------
    d : date
        Gregorian date (local calendar day).
    latitude, longitude : float
        Geographic coordinates in degrees.
    std_meridian : float
        Standard time meridian in degrees (e.g., 86.25 for UTC+5:45).
    elevation : float | None
        Elevation in meters (used if topocentric mode enabled).
    ephe_dir : str | None
        Optional ephemeris data directory (passed to Swiss Ephemeris).
    use_topocentric : bool
        If True, compute topocentric positions; otherwise geocentric.

    Returns
    -------
    DailyGrahas
        Dataclass with sunrise, Julian days, and graha positions/speeds.
    """

    # Sunrise in local standard time
    sunrise = sunrise_local(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
    )

    # 06:00 local standard time
    tz_std = _std_timezone(std_meridian)
    six_local = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=tz_std)

    six_utc = six_local.astimezone(timezone.utc)
    jd_ut_6 = _utc_julian_day(six_utc)

    sunrise_utc = sunrise.event_utc
    jd_ut_sunrise = _utc_julian_day(sunrise_utc)

    graha_spashta: Dict[str, float] = {}
    suryodaya_spashta: Dict[str, float] = {}
    graha_gati: Dict[str, float] = {}

    lat_topo = latitude if use_topocentric else None
    lon_topo = longitude if use_topocentric else None

    for graha_name in GRAHAS:
        # At 06:00 local time
        lon6, lat6, r6, lon_spd6, lat_spd6, r_spd6 = calc_graha(
            graha_name,
            jd_ut_6,
            latitude=lat_topo,
            longitude=lon_topo,
            elevation=elevation,
            ephe_dir=ephe_dir,
        )
        graha_spashta[graha_name] = float(norm_360(lon6))
        graha_gati[graha_name] = float(lon_spd6)

        # At sunrise
        lonsr, latsr, rsr, lon_spdsr, lat_spdsr, r_spdsr = calc_graha(
            graha_name,
            jd_ut_sunrise,
            latitude=lat_topo,
            longitude=lon_topo,
            elevation=elevation,
            ephe_dir=ephe_dir,
        )
        suryodaya_spashta[graha_name] = float(norm_360(lonsr))

    return DailyGrahas(
        date=d,
        latitude=float(latitude),
        longitude=float(longitude),
        std_meridian=float(std_meridian),
        sunrise=sunrise,
        jd_ut_6=jd_ut_6,
        jd_ut_sunrise=jd_ut_sunrise,
        graha_spashta=graha_spashta,
        suryodaya_spashta=suryodaya_spashta,
        graha_gati=graha_gati,
    )


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.engines.drik.grahas.calc_grahas)
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running calc_grahas self-tests...")

    from datetime import date as _d

    # Kathmandu sample: 2025-01-01
    d_test = _d(2025, 1, 1)
    lat_ktm = 27.7172
    lon_ktm = 85.3240
    std_meridian_ktm = 86.25  # UTC+5:45

    daily = daily_grahas(
        d_test,
        latitude=lat_ktm,
        longitude=lon_ktm,
        std_meridian=std_meridian_ktm,
        elevation=1300.0,
        ephe_dir=None,
        use_topocentric=True,
    )

    print("\n[ DailyGrahas summary ]")
    print("date           :", daily.date)
    print("latitude       :", daily.latitude)
    print("longitude      :", daily.longitude)
    print("std_meridian   :", daily.std_meridian)
    print("sunrise_local  :", daily.sunrise.event_local)
    print("jd_ut_6        :", daily.jd_ut_6)
    print("jd_ut_sunrise  :", daily.jd_ut_sunrise)

    # Basic sanity: sunrise and 06:00 JD are on the same UT day, close-ish
    assert abs(daily.jd_ut_6 - daily.jd_ut_sunrise) < 1.0

    # Check all grahas present and longitudes in range
    for g in GRAHAS:
        assert g in daily.graha_spashta
        assert g in daily.suryodaya_spashta
        assert g in daily.graha_gati

        lon6 = daily.graha_spashta[g]
        lonsr = daily.suryodaya_spashta[g]
        spd = daily.graha_gati[g]

        assert 0.0 <= lon6 < 360.0
        assert 0.0 <= lonsr < 360.0
        # speeds can be positive/negative, but should be finite numbers
        assert isinstance(spd, float)

    # Rahu / Ketu check at 06:00: roughly opposite
    rahu_lon = daily.graha_spashta["rahu"]
    ketu_lon = daily.graha_spashta["ketu"]
    expected_ketu = (rahu_lon + 180.0) % 360.0

    # Minimal signed angular difference in [-180, 180]
    delta = (ketu_lon - expected_ketu + 180.0) % 360.0 - 180.0
    diff = abs(delta)

    print("\n[ Rahu/Ketu @ 06:00 ]")
    print("rahu_lon =", rahu_lon)
    print("ketu_lon =", ketu_lon)
    print("expected ketu_lon ≈", expected_ketu)
    print("angular diff       =", diff)

    assert diff < 1e-3  # small tolerance

    print("\nAll calc_grahas self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()
