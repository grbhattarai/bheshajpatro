# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date
from math import isfinite

from bheshajpatro.core.core_functions import calc_shaka_year, calc_bhuja

__all__ = [
    "beeja_rahu",
    "beeja_gs",
    "calc_beeja",
    "calc_beeja_from_date",
]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _to_float_finite(value: float | int) -> float:
    """Convert to float and ensure the value is finite."""
    v = float(value)
    if not isfinite(v):
        raise TypeError("value must be a finite number")
    return v


# ----------------------------------------------------------------------
# Rahu beeja (traditional chandra-beeja chain)
# ----------------------------------------------------------------------

def beeja_rahu(shaka_year: float | int) -> float:
    y = _to_float_finite(shaka_year)

    shakantar = (y - 1800.0) / 100.0
    chandra_beeja = (shakantar * shakantar) / 6.0
    chandra_beeja /= 60.0
    rahu_beeja = chandra_beeja - (chandra_beeja / 4.0)

    return round(rahu_beeja, 12)


# ----------------------------------------------------------------------
# Guru / Śani beeja
# ----------------------------------------------------------------------

def calc_beeja(shaka_year: float | int) -> dict[str, float]:

    y = _to_float_finite(shaka_year)

    # Rahu
    rahu = beeja_rahu(y)

    # Guru / Śani chain
    beeja_bhagana = (y - 1481.0) % 918.0
    beeja_kendra = 30.0 * beeja_bhagana * (2.0 / 153.0)

    # Use imported calc_bhuja from core_functions
    beeja_bhujamsha = _to_float_finite(calc_bhuja(beeja_kendra))

    x = beeja_bhujamsha / 9.0
    base = (20.0 - x) * x

    mag = abs(base)
    guru_mins = mag / 5.0
    shani_mins = mag / 2.0

    k = beeja_kendra % 360.0

    if k > 180.0:
        guru_mins = -guru_mins
    else:
        shani_mins = -shani_mins

    guru = round(guru_mins / 60.0, 12)
    shani = round(shani_mins / 60.0, 12)

    return {"rahu": rahu, "guru": guru, "shani": shani}


def beeja_gs(graha: str, shaka_year: float | int) -> float:
    g = graha.strip().lower()
    if g not in ("guru", "shani"):
        raise ValueError("graha must be 'guru' or 'shani'")
    return calc_beeja(shaka_year)[g]


# ----------------------------------------------------------------------
# Convenience: compute beeja directly from a Gregorian date
# ----------------------------------------------------------------------

def calc_beeja_from_date(for_date: date) -> dict[str, float]:
    shaka_year = calc_shaka_year(for_date)
    return calc_beeja(shaka_year)


# ----------------------------------------------------------------------
# Simple local test
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # Example: directly from Shaka year
    sample_shaka_year = 1947
    print("From Shaka year:", calc_beeja(sample_shaka_year))

    print("\n=== Loop: Jan 1 from 2025 to yyyy ===")
    for y in range(2025, 2027):
        d = date(y, 1, 1)
        result = calc_beeja_from_date(d)

        # print with 5 decimal places
        r = result
        print(
            f"{d}  →  Rahu={r['rahu']:.5f}, "
            f"Guru={r['guru']:.5f}, Śani={r['shani']:.5f}"
        )