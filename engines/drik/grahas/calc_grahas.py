# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

# =============================================================================
# DEV OVERRIDE (REMOVE AFTER TESTING)
# -----------------------------------------------------------------------------
# Allows direct execution:
#     python engines/drik/grahas/calc_grahas.py
# =============================================================================
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    PACKAGE_PARENT = Path(__file__).resolve().parents[4]
    if str(PACKAGE_PARENT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_PARENT))
# =============================================================================

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

    Sunrise values are the primary Panchanga anchor.
    06:00 values are retained as a reference/debug bridge during migration.
    """

    date: _date
    latitude: float
    longitude: float
    std_meridian: float

    sunrise: SunEvent

    jd_ut_6: float
    jd_ut_sunrise: float

    graha_spashta_6: Dict[str, float]
    graha_gati_6: Dict[str, float]

    suryodaya_spashta: Dict[str, float]
    suryodaya_gati: Dict[str, float]


def _std_timezone(std_meridian: float) -> timezone:
    offset_hours = std_meridian / 15.0
    return timezone(timedelta(hours=offset_hours))


def _utc_julian_day(dt_utc: datetime) -> float:
    """
    Swiss-free Julian Day calculation (Gregorian calendar).
    """
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
        + d
        + b
        - 1524.5
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
    """
    Compute daily graha data for 06:00 and local sunrise.

    Panchanga-facing values are:
        - suryodaya_spashta
        - suryodaya_gati
    """

    sunrise = sunrise_local(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
    )

    tz_std = _std_timezone(std_meridian)
    six_local = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=tz_std)

    six_utc = six_local.astimezone(timezone.utc)
    jd_ut_6 = _utc_julian_day(six_utc)

    sunrise_utc = sunrise.event_utc
    jd_ut_sunrise = _utc_julian_day(sunrise_utc)

    graha_spashta_6: Dict[str, float] = {}
    graha_gati_6: Dict[str, float] = {}

    suryodaya_spashta: Dict[str, float] = {}
    suryodaya_gati: Dict[str, float] = {}

    lat_topo = latitude if use_topocentric else None
    lon_topo = longitude if use_topocentric else None

    for graha_name in GRAHAS:
        lon6, _lat6, _dist6, lon_spd6, _lat_spd6, _dist_spd6 = calc_graha(
            graha_name,
            jd_ut_6,
            latitude=lat_topo,
            longitude=lon_topo,
            elevation=elevation,
        )
        graha_spashta_6[graha_name] = float(norm_360(lon6))
        graha_gati_6[graha_name] = float(lon_spd6)

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
        jd_ut_6=jd_ut_6,
        jd_ut_sunrise=jd_ut_sunrise,
        graha_spashta_6=graha_spashta_6,
        graha_gati_6=graha_gati_6,
        suryodaya_spashta=suryodaya_spashta,
        suryodaya_gati=suryodaya_gati,
    )


def _run_self_tests() -> None:
    print("Running calc_grahas self-tests...")

    from datetime import date as _d

    d_test = _d(2025, 1, 1)
    lat_ktm = 27.7172
    lon_ktm = 85.3240
    std_meridian_ktm = 86.25

    daily = daily_grahas(
        d_test,
        latitude=lat_ktm,
        longitude=lon_ktm,
        std_meridian=std_meridian_ktm,
        elevation=1300.0,
        use_topocentric=True,
    )

    print("\n[ DailyGrahas summary ]")
    print("date             :", daily.date)
    print("latitude         :", daily.latitude)
    print("longitude        :", daily.longitude)
    print("std_meridian     :", daily.std_meridian)
    print("sunrise_local    :", daily.sunrise.event_local)
    print("jd_ut_6          :", daily.jd_ut_6)
    print("jd_ut_sunrise    :", daily.jd_ut_sunrise)

    assert abs(daily.jd_ut_6 - daily.jd_ut_sunrise) < 1.0

    for g in GRAHAS:
        assert g in daily.graha_spashta_6
        assert g in daily.graha_gati_6
        assert g in daily.suryodaya_spashta
        assert g in daily.suryodaya_gati

        lon6 = daily.graha_spashta_6[g]
        spd6 = daily.graha_gati_6[g]
        lonsr = daily.suryodaya_spashta[g]
        spdsr = daily.suryodaya_gati[g]

        assert 0.0 <= lon6 < 360.0
        assert 0.0 <= lonsr < 360.0
        assert isinstance(spd6, float)
        assert isinstance(spdsr, float)

    rahu_lon = daily.suryodaya_spashta["rahu"]
    ketu_lon = daily.suryodaya_spashta["ketu"]
    expected_ketu = (rahu_lon + 180.0) % 360.0
    delta = (ketu_lon - expected_ketu + 180.0) % 360.0 - 180.0
    diff = abs(delta)

    print("\n[ Rahu/Ketu @ sunrise ]")
    print("rahu_lon =", rahu_lon)
    print("ketu_lon =", ketu_lon)
    print("expected ketu_lon ≈", expected_ketu)
    print("angular diff       =", diff)

    assert diff < 1e-3

    print("\n[ Sunrise anchor sample ]")
    print("surya   lon/gati:", daily.suryodaya_spashta["surya"], daily.suryodaya_gati["surya"])
    print("chandra lon/gati:", daily.suryodaya_spashta["chandra"], daily.suryodaya_gati["chandra"])
    print("guru    lon/gati:", daily.suryodaya_spashta["guru"], daily.suryodaya_gati["guru"])
    print("shukra  lon/gati:", daily.suryodaya_spashta["shukra"], daily.suryodaya_gati["shukra"])
    print("shani  lon/gati:", daily.suryodaya_spashta["shani"], daily.suryodaya_gati["shani"])
    print("mangal  lon/gati:", daily.suryodaya_spashta["mangal"], daily.suryodaya_gati["mangal"])
    print("budha  lon/gati:", daily.suryodaya_spashta["budha"], daily.suryodaya_gati["budha"])
    print("rahu  lon/gati:", daily.suryodaya_spashta["rahu"], daily.suryodaya_gati["rahu"])
    print("ketu  lon/gati:", daily.suryodaya_spashta["ketu"], daily.suryodaya_gati["ketu"])

    print("\nAll calc_grahas self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()