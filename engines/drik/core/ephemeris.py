# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Generic ephemeris interface for the drik engine.
#
# This module is intentionally Swiss-free. It preserves the useful public API
# and graha naming conventions from the old wrapper, while deferring actual
# astronomy computations to a backend implementation.

from __future__ import annotations

from typing import Dict, Final, Protocol, Tuple

__all__ = [
    "CANONICAL_GRAHAS",
    "GRAHA_NAME_ALIASES",
    "GrahaResult",
    "calc_graha",
    "set_backend",
    "get_backend",
]


# Canonical graha names (Hindu traditional)
CANONICAL_GRAHAS: Final[list[str]] = [
    "surya",
    "chandra",
    "mangal",
    "budha",
    "guru",
    "shukra",
    "shani",
    "rahu",
    "ketu",
]

GRAHA_NAME_ALIASES: Final[Dict[str, str]] = {
    # Surya
    "surya": "surya",
    "sun": "surya",
    "ravi": "surya",
    # Chandra
    "chandra": "chandra",
    "chandrama": "chandra",
    "moon": "chandra",
    # Mangal
    "mangal": "mangal",
    "mars": "mangal",
    "mangala": "mangal",
    # Budha
    "budha": "budha",
    "mercury": "budha",
    # Guru
    "guru": "guru",
    "brihaspati": "guru",
    "jupiter": "guru",
    # Shukra
    "shukra": "shukra",
    "venus": "shukra",
    # Shani
    "shani": "shani",
    "saturn": "shani",
    # Rahu / Ketu
    "rahu": "rahu",
    "north_node": "rahu",
    "ascending_node": "rahu",
    "ketu": "ketu",
    "south_node": "ketu",
    "descending_node": "ketu",
}

GrahaResult = Tuple[
    float,  # nirayana longitude
    float,  # latitude
    float,  # distance
    float,  # longitude speed (deg/day)
    float,  # latitude speed (deg/day)
    float,  # distance speed (units/day)
]


class EphemerisBackend(Protocol):
    """
    Interface that any astronomy backend must implement.

    Returned tuple must be:
        (
            nirayana_longitude_deg,
            latitude_deg,
            distance,
            longitude_speed_deg_per_day,
            latitude_speed_deg_per_day,
            distance_speed_per_day,
        )
    """

    def calc_graha(
        self,
        graha: str,
        jd_ut: float,
        latitude: float | None = None,
        longitude: float | None = None,
        elevation: float | None = 0.0,
    ) -> GrahaResult:
        ...


class _UnconfiguredBackend:
    """
    Default placeholder backend.

    This fails fast until a real Swiss-free ephemeris backend is plugged in.
    """

    def calc_graha(
        self,
        graha: str,
        jd_ut: float,
        latitude: float | None = None,
        longitude: float | None = None,
        elevation: float | None = 0.0,
    ) -> GrahaResult:
        raise NotImplementedError(
            "No ephemeris backend configured. "
            "Attach a Swiss-free backend with set_backend(...)."
        )


_BACKEND: EphemerisBackend = _UnconfiguredBackend()


def set_backend(backend: EphemerisBackend) -> None:
    """
    Register the active ephemeris backend.
    """
    global _BACKEND
    _BACKEND = backend


def get_backend() -> EphemerisBackend:
    """
    Return the currently active ephemeris backend.
    """
    return _BACKEND


def _angle_diff(deg_a: float, deg_b: float) -> float:
    """
    Smallest signed difference between two angles in degrees (-180, 180].
    """
    diff = (deg_a - deg_b) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


def _canonical_graha_name(graha: str) -> str:
    """
    Normalize graha name to canonical internal name.
    """
    key = graha.strip().lower()
    canonical = GRAHA_NAME_ALIASES.get(key)
    if canonical is None:
        raise ValueError(
            f"unsupported graha {graha!r}. "
            f"supported names include: {sorted(set(GRAHA_NAME_ALIASES.keys()))}"
        )
    return canonical


def calc_graha(
    graha: str,
    jd_ut: float,
    latitude: float | None = None,
    longitude: float | None = None,
    elevation: float | None = 0.0,
) -> GrahaResult:
    """
    Public graha calculation entry point.

    This preserves the old external API while delegating actual astronomy
    work to the configured backend.

    Parameters
    ----------
    graha:
        Traditional or English graha name, e.g. "surya", "sun", "chandra", "moon".
    jd_ut:
        Julian day in UT.
    latitude, longitude, elevation:
        Optional observer coordinates for topocentric calculations.

    Returns
    -------
    GrahaResult
        (
            nirayana_longitude,
            latitude,
            distance,
            longitude_speed,
            latitude_speed,
            distance_speed,
        )
    """
    canonical = _canonical_graha_name(graha)

    if canonical == "ketu":
        (
            rahu_lon,
            rahu_lat,
            rahu_dist,
            rahu_lon_speed,
            rahu_lat_speed,
            rahu_dist_speed,
        ) = _BACKEND.calc_graha(
            "rahu",
            jd_ut,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
        )
        ketu_lon = (rahu_lon + 180.0) % 360.0
        return (
            float(ketu_lon),
            float(-rahu_lat),
            float(rahu_dist),
            float(rahu_lon_speed),
            float(-rahu_lat_speed),
            float(rahu_dist_speed),
        )

    return _BACKEND.calc_graha(
        canonical,
        jd_ut,
        latitude=latitude,
        longitude=longitude,
        elevation=elevation,
    )