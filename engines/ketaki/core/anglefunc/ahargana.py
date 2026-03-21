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
    "calc_weekday",
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
    Compute reduced ahargana (1-based) and the number of completed 19-year cycles
    since the SHAKA_EPOCH.
    """
    if on_date < SHAKA_EPOCH:
        raise ValueError("date before Ketaki epoch")

    delta_days = (on_date - SHAKA_EPOCH).days

    cycles = 0
    cyc_days = 0
    cursor = SHAKA_EPOCH

    # Accumulate full 19-year cycles until the next cycle would exceed on_date.
    while True:
        nxt = _add_years_safe(cursor, CYCLE_YEARS)
        if nxt > on_date:
            break
        cyc_days += (nxt - cursor).days
        cursor = nxt
        cycles += 1

    # Reduced ahargana (1-based).
    reduced = 1 + (delta_days - cyc_days)

    # Align such that the epoch weekday fits into a 7-day cycle nicely.
    corr = cyc_days % 7
    aligned = reduced - ((7 - corr) % 7)
    while aligned <= 0:
        aligned += 7

    return cycles, float(round(aligned, 10))


def project_to_longitude(ahargana_ujjain: float, local_longitude: float) -> float:
    """Project ahargana from Ujjain longitude to a local longitude."""
    dlon = float(local_longitude) - float(UJJAIN_LONGITUDE)
    return float(round(ahargana_ujjain - (dlon / 360.0), 10))


def calc_weekday(ahargana_ujjain: float) -> tuple[int, str]:
    """
    Return weekday index and name from ahargana at Ujjain.

    Index mapping:
    0 -> wednesday, 1 -> thursday, ..., 6 -> tuesday
    """
    idx = int(ahargana_ujjain) % 7
    labels = (
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "monday",
        "tuesday",
    )
    return idx, labels[idx]


def compute_ahargana(*, place: dict[str, object], for_date: date) -> dict[str, object]:
    """
    High-level helper to compute ahargana and metadata for a given place & date.
    """
    lat = float(place.get("latitude", 0.0))
    lon = float(place.get("longitude", 0.0))
    std_meridian = float(place.get("std_meridian", 0.0))

    shaka_year = calc_shaka_year(for_date)
    chakra_cnt, ah_ujjain = calc_reduced_ahargana(for_date)
    ah_local = project_to_longitude(ah_ujjain, lon)
    wd_idx, wd_name = calc_weekday(ah_ujjain)

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
        "weekday_index": wd_idx,
        "weekday_name": wd_name,
    }


if __name__ == "__main__":
    # Example location: Kathmandu (adjust as needed).
    sample_place = {
        "city": "Kathmandu",
        "latitude": 27.7172,
        "longitude": 85.3240,
        # Nepal standard meridian (UTC+5:45) ≈ 86.25° E
        "std_meridian": 86.25,
        "tz": "Asia/Kathmandu",
    }

    sample_date = date(2025, 3, 30)

    result = compute_ahargana(place=sample_place, for_date=sample_date)

    print("=== Ketaki ahargana sample ===")
    for key, value in result.items():
        print(f"{key}: {value}")

    greg_idx = sample_date.weekday()
    greg_labels = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    print("\n=== Gregorian weekday check ===")
    print(f"date: {sample_date.isoformat()}")
    print(f"gregorian_weekday_index: {greg_idx}")
    print(f"gregorian_weekday_name: {greg_labels[greg_idx]}")
    print(f"ketaki_weekday_index: {result['weekday_index']}")
    print(f"ketaki_weekday_name: {result['weekday_name']}")
