# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date

from bheshajpatro.core.core_functions import calc_shaka_year

UJJAIN_LONGITUDE = 75.784912
SHAKA_EPOCH = date(1878, 4, 4)
CYCLE_YEARS = 19

__all__ = [
    "calc_reduced_ahargana",
    "project_to_longitude",
    "compute_ahargana",
]


def _add_years_safe(d: date, years: int) -> date:
    """Add years to a date, clamping the day down for leap-year edge cases."""
    y, m, day = d.year + years, d.month, d.day
    while True:
        try:
            return date(y, m, day)
        except ValueError:
            day -= 1


def calc_reduced_ahargana(on_date: date) -> tuple[int, float]:
    """
    Compute reduced ahargana (1-based) and completed 19-year cycles
    since the Ketaki epoch.
    """
    if on_date < SHAKA_EPOCH:
        raise ValueError("date before Ketaki epoch")

    delta_days = (on_date - SHAKA_EPOCH).days

    cycles = 0
    cyc_days = 0
    cursor = SHAKA_EPOCH

    while True:
        nxt = _add_years_safe(cursor, CYCLE_YEARS)
        if nxt > on_date:
            break
        cyc_days += (nxt - cursor).days
        cursor = nxt
        cycles += 1

    reduced = 1 + (delta_days - cyc_days)

    corr = cyc_days % 7
    aligned = reduced - ((7 - corr) % 7)
    while aligned <= 0:
        aligned += 7

    return cycles, float(round(aligned, 10))


def project_to_longitude(ahargana_ujjain: float, local_longitude: float) -> float:
    """Project ahargana from Ujjain longitude to local longitude."""
    dlon = float(local_longitude) - float(UJJAIN_LONGITUDE)
    return float(round(ahargana_ujjain - (dlon / 360.0), 10))


def compute_ahargana(*, place: dict[str, object], for_date: date) -> dict[str, object]:
    """
    Compute ahargana and core metadata for a given place and date.
    """
    lat = float(place.get("latitude", 0.0))
    lon = float(place.get("longitude", 0.0))
    std_meridian = float(place.get("std_meridian", place.get("standard", 0.0)))

    shaka_year = calc_shaka_year(for_date)
    chakra_cnt, ah_ujjain = calc_reduced_ahargana(for_date)
    ah_local = project_to_longitude(ah_ujjain, lon)

    return {
        "date": for_date.isoformat(),
        "place": {
            "city": place.get("city"),
            "latitude": lat,
            "longitude": lon,
            "std_meridian": std_meridian,
            "tz": place.get("tz"),
        },
        "method": "ketaki",
        "shaka_year": shaka_year,
        "chakra_cnt": chakra_cnt,
        "ahargana_ujjain": ah_ujjain,
        "ahargana": ah_local,
    }