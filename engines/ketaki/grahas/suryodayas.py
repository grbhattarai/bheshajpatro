# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import math

from bheshajpatro.core.core_functions import norm_360, calc_shadvalpa
from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import calc_phalanka

__all__ = [
    "ayanamsha",
    "surya_sayana",
    "surya_kranti",
    "chara",
    "belantara",
    "deshantara",
    "dhupaghadi",
    "local_sunrise",
    "std_sunrise",
    "chalana",
    "sunrise_adjust",
]


# ----------------------------------------------------------------------
# AYANAMSHA + SAYANA LONGITUDE
# ----------------------------------------------------------------------


def ayanamsha(shaka_year: float) -> float:
    """Compute ayanamsha (deg) for a given Shaka year."""
    year = float(shaka_year)
    return 22.1425 + (year - 1800.0) * ((1.0 / 70.0) - (1.0 / 3000.0))


def surya_sayana(surya_nirayana: float, ayanamsha_deg: float) -> float:
    """Convert nirayana longitude to sayana longitude."""
    return norm_360(float(surya_nirayana) + float(ayanamsha_deg))


# ----------------------------------------------------------------------
# KRANTI (DECLINATION)
# ----------------------------------------------------------------------


def surya_kranti(surya_sayana_deg: float) -> float:
    """
    Compute solar declination (kranti) from sayana longitude.

    Uses shadvalpa + phalanka table "suryakranti" (values in decaminutes).
    """
    sv = calc_shadvalpa(float(surya_sayana_deg))
    ph = calc_phalanka("suryakranti", "surya", sv)
    return ph / 60.0  # table values are in decaminutes


# ----------------------------------------------------------------------
# CHARA (LATITUDE × DECLINATION)
# ----------------------------------------------------------------------


def chara(latitude: float, kranti: float) -> tuple[float, float]:
    """
    Compute chara: effect of latitude × declination.

    Returns (hours, minutes).
    """
    lat = max(min(float(latitude), 89.999), -89.999)
    tan_lat = math.tan(math.radians(lat))
    tan_kra = math.tan(math.radians(float(kranti)))
    hours = tan_lat * tan_kra * 4.0
    return hours, hours * 60.0


# ----------------------------------------------------------------------
# EQUATION OF TIME (BELANTARA)
# ----------------------------------------------------------------------


def belantara(surya_sayana_deg: float) -> tuple[float, float]:
    """
    Equation of time (belantara) from sayana longitude.

    Returns (hours, minutes).
    """
    s = float(surya_sayana_deg) % 360.0
    minutes = (
        9.87 * math.sin(math.radians(2 * s))
        - 7.53 * math.cos(math.radians(s))
        - 1.5 * math.sin(math.radians(s))
    )
    return minutes / 60.0, minutes


# ----------------------------------------------------------------------
# LONGITUDE-TIME CORRECTION (DESHANTARA)
# ----------------------------------------------------------------------


def deshantara(longitude: float, standard_meridian: float) -> float:
    """
    Time correction (hours) for difference between local longitude and
    standard meridian.
    """
    return (float(standard_meridian) - float(longitude)) / 15.0


# ----------------------------------------------------------------------
# DHUPAGHADI + SUNRISE TIME
# ----------------------------------------------------------------------


def dhupaghadi(
    *,
    latitude: float,
    surya_sayana_deg: float,
    chara_hours: float,
) -> float:
    """
    Compute dhupaghadi (solar rise time from 6h reference).

    Returns hours from midnight (local mean time).
    """
    lat = float(latitude)
    say = float(surya_sayana_deg)
    ch = float(chara_hours)

    negative = (lat > 0 and say < 180.0) or (lat < 0 and say >= 180.0)
    adjust = -ch if negative else ch

    return 6.0 + adjust


def local_sunrise(
    *,
    latitude: float,
    surya_sayana_deg: float,
    chara_hours: float,
    belantara_hours: float,
) -> float:
    """
    Local sunrise time (hours, local mean time) before deshantara correction.
    """
    dh = dhupaghadi(
        latitude=latitude,
        surya_sayana_deg=surya_sayana_deg,
        chara_hours=chara_hours,
    )
    return dh - float(belantara_hours)


def std_sunrise(
    *,
    local_sunrise_hours: float,
    deshantara_hours: float,
) -> float:
    """Standard-time sunrise in hours."""
    return float(local_sunrise_hours) + float(deshantara_hours)


# ----------------------------------------------------------------------
# CHALANA (NET MINUTE ADJUSTMENT)
# ----------------------------------------------------------------------


def chalana(
    *,
    chara_mins: float,
    belantara_mins: float,
    latitude: float,
    surya_sayana_deg: float,
) -> float:
    """
    Net minute adjustment (chalana) combining chara and belantara.
    """
    lat = float(latitude)
    say = float(surya_sayana_deg)

    negative_chara = (lat > 0 and say < 180.0) or (lat < 0 and say > 180.0)

    adj_chara = -float(chara_mins) if negative_chara else float(chara_mins)
    adj_bel = -float(belantara_mins)

    return adj_chara + adj_bel


# ----------------------------------------------------------------------
# SPASHTA CORRECTION (FINAL SUNRISE-LONGITUDE ADJUSTMENT)
# ----------------------------------------------------------------------


def sunrise_adjust(
    *,
    spashta: float,
    gati_per_day: float,
    chalana_mins: float,
) -> tuple[float, float, float]:
    """
    Apply final sunrise-longitude adjustment to solar spashta.

    Returns (final_spashta_deg, raw_delta_deg, signed_delta_deg).
    """
    c = float(chalana_mins)
    g = float(gati_per_day)

    raw = (c * g) / 1440.0  # 1440 minutes in a day

    same_sign = c == 0.0 or g == 0.0 or ((c > 0.0) == (g > 0.0))
    adj = raw if same_sign else -abs(raw)

    final = norm_360(float(spashta) + adj)
    return final, raw, adj
