# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Pure-Python prototype ephemeris backend for the drik engine.
#
# Notes
# -----
# - No third-party astronomy package dependency
# - No Swiss Ephemeris dependency
# - Designed to plug into core/ephemeris.py
# - Good enough for prototype wiring
# - This is NOT a full Moshier-accuracy implementation yet

from __future__ import annotations

from math import cos, radians, sin
from typing import Final

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.drik.core.ephemeris import GrahaResult, set_backend

__all__ = [
    "PurePythonEphemerisBackend",
]

J2000: Final[float] = 2451545.0


def _sin_deg(x: float) -> float:
    return sin(radians(x))


def _cos_deg(x: float) -> float:
    return cos(radians(x))


def _angle_diff(deg_a: float, deg_b: float) -> float:
    """
    Smallest signed angular difference between two angles in degrees.
    Result in (-180, 180].
    """
    diff = (deg_a - deg_b) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


def _julian_centuries(jd_ut: float) -> float:
    return (jd_ut - J2000) / 36525.0


def _lahiri_ayanamsha_deg_approx(jd_ut: float) -> float:
    """
    Approximate Lahiri ayanamsha in degrees.

    Prototype approximation:
    - anchored near J2000
    - linear precession rate

    This is sufficient for a prototype backend, but should be refined later.
    """
    days = jd_ut - J2000
    ayan_j2000 = 23.8530556
    rate_deg_per_day = 50.290966 / 3600.0 / 365.242189
    return ayan_j2000 + days * rate_deg_per_day


def _sun_tropical_longitude(jd_ut: float) -> float:
    """
    Approximate apparent geocentric tropical longitude of the Sun.
    """
    T = _julian_centuries(jd_ut)

    L0 = norm_360(280.46646 + 36000.76983 * T + 0.0003032 * T * T)
    M = norm_360(357.52911 + 35999.05029 * T - 0.0001537 * T * T)

    C = (
        (1.914602 - 0.004817 * T - 0.000014 * T * T) * _sin_deg(M)
        + (0.019993 - 0.000101 * T) * _sin_deg(2.0 * M)
        + 0.000289 * _sin_deg(3.0 * M)
    )

    true_long = L0 + C
    omega = 125.04 - 1934.136 * T
    apparent_long = true_long - 0.00569 - 0.00478 * _sin_deg(omega)
    return norm_360(apparent_long)


def _moon_tropical_longitude_latitude_distance(jd_ut: float) -> tuple[float, float, float]:
    """
    Approximate geocentric tropical longitude/latitude/distance of the Moon.

    Compact low-order series, good enough for prototype work.
    """
    T = _julian_centuries(jd_ut)

    Lp = norm_360(
        218.3164477
        + 481267.88123421 * T
        - 0.0015786 * T * T
        + T * T * T / 538841.0
        - T * T * T * T / 65194000.0
    )
    D = norm_360(
        297.8501921
        + 445267.1114034 * T
        - 0.0018819 * T * T
        + T * T * T / 545868.0
        - T * T * T * T / 113065000.0
    )
    M = norm_360(
        357.5291092
        + 35999.0502909 * T
        - 0.0001536 * T * T
        + T * T * T / 24490000.0
    )
    Mp = norm_360(
        134.9633964
        + 477198.8675055 * T
        + 0.0087414 * T * T
        + T * T * T / 69699.0
        - T * T * T * T / 14712000.0
    )
    F = norm_360(
        93.2720950
        + 483202.0175233 * T
        - 0.0036539 * T * T
        - T * T * T / 3526000.0
        + T * T * T * T / 863310000.0
    )

    lon = Lp + (
        6.289 * _sin_deg(Mp)
        + 1.274 * _sin_deg(2.0 * D - Mp)
        + 0.658 * _sin_deg(2.0 * D)
        + 0.214 * _sin_deg(2.0 * Mp)
        - 0.186 * _sin_deg(M)
        - 0.114 * _sin_deg(2.0 * F)
    )

    lat = (
        5.128 * _sin_deg(F)
        + 0.280 * _sin_deg(Mp + F)
        + 0.277 * _sin_deg(Mp - F)
        + 0.173 * _sin_deg(2.0 * D - F)
        + 0.055 * _sin_deg(2.0 * D + F - Mp)
        + 0.046 * _sin_deg(2.0 * D - F - Mp)
        + 0.033 * _sin_deg(2.0 * D + F)
        + 0.017 * _sin_deg(2.0 * Mp + F)
    )

    distance_km = (
        385000.56
        - 20905.0 * _cos_deg(Mp)
        - 3699.0 * _cos_deg(2.0 * D - Mp)
        - 2956.0 * _cos_deg(2.0 * D)
        - 570.0 * _cos_deg(2.0 * Mp)
    )

    return norm_360(lon), float(lat), float(distance_km)


def _mean_node_tropical_longitude(jd_ut: float) -> float:
    """
    Mean ascending node (Rahu) in tropical longitude.
    """
    T = _julian_centuries(jd_ut)
    omega = (
        125.0445550
        - 1934.1361849 * T
        + 0.0020762 * T * T
        + T * T * T / 467410.0
        - T * T * T * T / 60616000.0
    )
    return norm_360(omega)


# Very rough prototype mean tropical longitudes for classical planets.
# These are placeholders for app wiring until a fuller backend is built.
_PLANET_MEAN_LONGITUDE_J2000: Final[dict[str, float]] = {
    "mangal": 355.433,
    "budha": 252.251,
    "guru": 34.351,
    "shukra": 181.979,
    "shani": 50.077,
}

_PLANET_MEAN_RATE_DEG_PER_DAY: Final[dict[str, float]] = {
    "mangal": 0.524039,
    "budha": 4.092385,
    "guru": 0.083086,
    "shukra": 1.602130,
    "shani": 0.033459,
}


def _placeholder_planet_tropical_longitude(graha: str, jd_ut: float) -> float:
    """
    Coarse placeholder mean tropical longitude for prototype use.
    """
    d = jd_ut - J2000
    base = _PLANET_MEAN_LONGITUDE_J2000[graha]
    rate = _PLANET_MEAN_RATE_DEG_PER_DAY[graha]
    return norm_360(base + rate * d)


def _sidereal_longitude(tropical_longitude: float, jd_ut: float) -> float:
    ayan = _lahiri_ayanamsha_deg_approx(jd_ut)
    return norm_360(tropical_longitude - ayan)


def _finite_speed(
    longitude_fn,
    jd_ut: float,
    delta_days: float = 1.0 / 1440.0,
) -> float:
    """
    Estimate longitude speed in deg/day using a small finite difference.
    """
    lon1 = longitude_fn(jd_ut)
    lon2 = longitude_fn(jd_ut + delta_days)
    return _angle_diff(lon2, lon1) / delta_days


class PurePythonEphemerisBackend:
    """
    Swiss-free pure-Python prototype backend.
    """

    def calc_graha(
        self,
        graha: str,
        jd_ut: float,
        latitude: float | None = None,
        longitude: float | None = None,
        elevation: float | None = 0.0,
    ) -> GrahaResult:
        graha = graha.strip().lower()

        if graha == "surya":
            trop_lon = _sun_tropical_longitude(jd_ut)
            sid_lon = _sidereal_longitude(trop_lon, jd_ut)
            lon_speed = _finite_speed(_sun_tropical_longitude, jd_ut)
            return (float(sid_lon), 0.0, 1.0, float(lon_speed), 0.0, 0.0)

        if graha == "chandra":
            trop_lon, lat_deg, dist_km = _moon_tropical_longitude_latitude_distance(jd_ut)
            sid_lon = _sidereal_longitude(trop_lon, jd_ut)

            def moon_lon_fn(jd: float) -> float:
                lon, _, _ = _moon_tropical_longitude_latitude_distance(jd)
                return lon

            def moon_lat_fn(jd: float) -> float:
                _, lat, _ = _moon_tropical_longitude_latitude_distance(jd)
                return lat

            def moon_dist_fn(jd: float) -> float:
                _, _, dist = _moon_tropical_longitude_latitude_distance(jd)
                return dist

            delta = 1.0 / 1440.0
            lon_speed  = _angle_diff(moon_lon_fn(jd_ut + delta), moon_lon_fn(jd_ut)) / delta
            lat_speed  = (moon_lat_fn(jd_ut + delta) - moon_lat_fn(jd_ut)) / delta
            dist_speed = (moon_dist_fn(jd_ut + delta) - moon_dist_fn(jd_ut)) / delta

            return (
                float(sid_lon), float(lat_deg), float(dist_km),
                float(lon_speed), float(lat_speed), float(dist_speed),
            )

        if graha == "rahu":
            trop_lon = _mean_node_tropical_longitude(jd_ut)
            sid_lon = _sidereal_longitude(trop_lon, jd_ut)
            lon_speed = _finite_speed(_mean_node_tropical_longitude, jd_ut)
            return (float(sid_lon), 0.0, 1.0, float(lon_speed), 0.0, 0.0)

        if graha in _PLANET_MEAN_LONGITUDE_J2000:
            trop_lon = _placeholder_planet_tropical_longitude(graha, jd_ut)
            sid_lon = _sidereal_longitude(trop_lon, jd_ut)

            def planet_lon_fn(jd: float) -> float:
                return _placeholder_planet_tropical_longitude(graha, jd)

            lon_speed = _finite_speed(planet_lon_fn, jd_ut)
            return (float(sid_lon), 0.0, 1.0, float(lon_speed), 0.0, 0.0)

        raise ValueError(f"unsupported graha: {graha!r}")


set_backend(PurePythonEphemerisBackend())