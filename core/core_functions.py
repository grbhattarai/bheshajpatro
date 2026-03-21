# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Core math helpers shared by drik/ketaki engines:
#  - angle normalization and derived quantities
#  - rashi ↔ degree conversions
#  - time/ghati conversions
#  - date → shaka year


from __future__ import annotations
from typing import Tuple
from datetime import date

__all__ = [
    # angle helpers
    "norm_360",
    "calc_bhuja",
    "calc_koti",
    "calc_shadvalpa",
    # rashi/degree conversions
    "rashi_to_deg",
    "deg_to_rashi",
    # time conversions
    "hour_to_hms",
    "hour_to_hm",
    "ghati_to_gp",
    "ghati_to_gpb",
    # date to shaka year
    "calc_shaka_year",
]

# ----------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------

# Small epsilon to stabilize floating-point edge cases
EPSILON = 1e-12

# Rashi / degree constants
ARCSEC_PER_DEG = 3600
ARCSEC_PER_RASHI = 30 * ARCSEC_PER_DEG       # 30 degrees per rashi
ARCSEC_FULL = 360 * ARCSEC_PER_DEG           # full circle = 360 degrees

# Time constants
SEC_PER_HOUR = 3600
SEC_PER_DAY = 24 * SEC_PER_HOUR              # 86_400
MIN_PER_DAY = 24 * 60                        # 1_440

PALA_PER_GHATI = 60
BIPALA_PER_PALA = 60
BIPALA_PER_GHATI = PALA_PER_GHATI * BIPALA_PER_PALA  # 3_600
BIPALA_PER_DAY = 60 * BIPALA_PER_GHATI               # 216_000

# Type alias for a rashi angle (rashi, amsha, kala, bikala)
RashiCoord = Tuple[int, int, int, int]


# ----------------------------------------------------------------------
# ANGLE HELPERS
# ----------------------------------------------------------------------

def norm_360(angle: float) -> float:
    """
    Normalize any angle to [0, 360), avoiding tiny floating drift around zero.
    """
    val = (float(angle) % 360.0 + EPSILON) % 360.0

    # clean small values like 1e-12 to exactly 0.0
    if abs(val) < 1e-9:
        return 0.0
    return val


def calc_bhuja(angle: float) -> float:
    """
    Bhuja: acute angle measured from 0/180 line (0–90).
    """
    deg = norm_360(angle)

    if deg < 90.0:
        return deg
    if deg < 180.0:
        return 180.0 - deg
    if deg < 270.0:
        return deg - 180.0
    return 360.0 - deg


def calc_koti(angle: float) -> float:
    """
    Koti: complement of bhuja, clamped to [0, 90].
    """
    val = 90.0 - calc_bhuja(angle)

    if val < 0.0:
        return 0.0
    if val > 90.0:
        return 90.0
    return val


def calc_shadvalpa(angle: float) -> float:
    """
    Shortest distance to 0° (0–180).
    """
    deg = norm_360(angle)
    return deg if deg <= 180.0 else 360.0 - deg


# ----------------------------------------------------------------------
# RASHI / DEGREE CONVERSIONS
# ----------------------------------------------------------------------

def rashi_to_deg(rashi_input: RashiCoord) -> float:
    """
    Convert (rashi, amsha, kala, bikala) → degrees [0, 360).

    rashi:   0–11 (0 = Mesha, 1 = Vrishabha, ...)
    amsha:   degrees within rashi
    kala:    minutes
    bikala:  seconds
    """
    rashi, amsha, kala, bikala = rashi_input

    total_deg = (
        rashi * 30.0            # each rashi is 30°
        + amsha                 # integer degrees
        + kala / 60.0           # minutes → degrees
        + bikala / 3600.0       # seconds → degrees
    )

    return (total_deg + EPSILON) % 360.0


def deg_to_rashi(degree: float) -> RashiCoord:
    """
    Convert degrees → (rashi, amsha, kala, bikala).

    Returns values normalized so that degree in [0,360) maps to:
      rashi:   0–11
      amsha:   0–29
      kala:    0–59
      bikala:  0–59
    """
    deg = (float(degree) + EPSILON) % 360.0

    # convert entire angle to arcseconds
    total_arcsec = int(round(deg * ARCSEC_PER_DEG)) % ARCSEC_FULL

    # decompose
    rashi, rem = divmod(total_arcsec, ARCSEC_PER_RASHI)
    amsha, rem = divmod(rem, ARCSEC_PER_DEG)
    kala, bikala = divmod(rem, 60)

    return int(rashi), int(amsha), int(kala), int(bikala)

# ----------------------------------------------------------------------
# SHAKA YEAR
# ----------------------------------------------------------------------

MARGIN_MONTH = 3
MARGIN_DAY = 28


def calc_shaka_year(d: date) -> int:
    """
    Return the Shaka year for a given Gregorian date.

    Rule:

        boundary = YYYY-03-28

        if d <= boundary:
            shaka = year - 79
        else:
            shaka = year - 78
    """
    boundary = date(d.year, MARGIN_MONTH, MARGIN_DAY)
    return d.year - 79 if d <= boundary else d.year - 78

# ----------------------------------------------------------------------
# TIME CONVERSIONS
# ----------------------------------------------------------------------

def _round_to_int(x: float, modulo: int | None = None) -> int:
    """
    Round a float to nearest int with small epsilon and optional modulo.
    """
    n = int(round(x + EPSILON))
    if modulo is not None:
        n %= modulo
    return n


def hour_to_hms(hour: float) -> str:
    """
    Convert fractional hours → 'HH:MM:SS' (24-hour clock).
    """
    h_float = float(hour) % 24.0
    total_sec = _round_to_int(h_float * SEC_PER_HOUR, SEC_PER_DAY)

    h, rem = divmod(total_sec, SEC_PER_HOUR)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def hour_to_hm(hour: float) -> str:
    """
    Convert fractional hours → 'HH:MM'.
    """
    h_float = float(hour) % 24.0
    total_min = _round_to_int(h_float * 60.0, MIN_PER_DAY)

    h, m = divmod(total_min, 60)
    return f"{h:02d}:{m:02d}"


def ghati_to_gp(ghati: float) -> str:
    """
    Convert ghati → 'GG:PP' (ghati:pala).
    """
    g_float = float(ghati) % 60.0
    total_pala = _round_to_int(g_float * PALA_PER_GHATI, 60 * PALA_PER_GHATI)

    g, p = divmod(total_pala, PALA_PER_GHATI)
    return f"{g:02d}:{p:02d}"


def ghati_to_gpb(ghati: float) -> str:
    """
    Convert ghati → 'GG:PP:BB' (ghati:pala:bipala).
    """
    g_float = float(ghati) % 60.0
    total_bipala = _round_to_int(g_float * BIPALA_PER_GHATI, BIPALA_PER_DAY)

    g, rem = divmod(total_bipala, BIPALA_PER_GHATI)
    p, b = divmod(rem, BIPALA_PER_PALA)
    return f"{g:02d}:{p:02d}:{b:02d}"


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.core.core_functions)
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running core_functions self-tests...")

    # --- norm_360 ------------------------------------------------------
    print("\n[ norm_360 samples ]")
    print("norm_360(0)        =", norm_360(0))
    print("norm_360(360)      =", norm_360(360))
    print("norm_360(-30)      =", norm_360(-30))
    print("norm_360(450)      =", norm_360(450))

    assert norm_360(0) == 0.0
    assert norm_360(360) == 0.0
    assert abs(norm_360(-30) - 330.0) < 1e-9
    assert abs(norm_360(450) - 90.0) < 1e-9

    # --- bhuja / koti --------------------------------------------------
    print("\n[ calc_bhuja / calc_koti samples ]")
    for a in (45, 135, 225, 315):
        print(f"angle={a:3d}  bhuja={calc_bhuja(a):6.2f}  koti={calc_koti(a):6.2f}")

    # For 45°, 135°, 225°, 315° the bhuja should be 45
    for a in (45, 135, 225, 315):
        assert abs(calc_bhuja(a) - 45.0) < 1e-9
        assert abs(calc_koti(a) - 45.0) < 1e-9

    # --- shadvalpa -----------------------------------------------------
    print("\n[ calc_shadvalpa samples ]")
    print("shadvalpa(10)      =", calc_shadvalpa(10))
    print("shadvalpa(190)     =", calc_shadvalpa(190))
    print("shadvalpa(350)     =", calc_shadvalpa(350))

    assert abs(calc_shadvalpa(10) - 10.0) < 1e-9
    assert abs(calc_shadvalpa(190) - 170.0) < 1e-9
    assert abs(calc_shadvalpa(350) - 10.0) < 1e-9

    # --- rashi ↔ deg roundtrip ----------------------------------------
    print("\n[ rashi_to_deg / deg_to_rashi samples ]")
    samples: list[RashiCoord] = [
        (0, 0, 0, 0),        # 0° Mesha
        (1, 0, 0, 0),        # 30° Vrishabha start
        (2, 15, 30, 0),      # random 2nd rashi
        (11, 29, 59, 59),    # just below 360°
    ]
    for s in samples:
        d = rashi_to_deg(s)
        back = deg_to_rashi(d)
        print(f"rashi={s}  -> deg={d:.6f}  -> back={back}")
        assert back == s, f"rashi roundtrip failed: {s} -> {d} -> {back}"

    # --- time conversions ----------------------------------------------
    print("\n[ hour_to_hms / hour_to_hm samples ]")
    print("hour_to_hms(0.0)   =", hour_to_hms(0.0))
    print("hour_to_hms(6.5)   =", hour_to_hms(6.5))
    print("hour_to_hm(1.5)    =", hour_to_hm(1.5))
    print("hour_to_hm(23.75)  =", hour_to_hm(23.75))

    assert hour_to_hms(0.0) == "00:00:00"
    # 6.5 hours = 06:30:00
    assert hour_to_hms(6.5) == "06:30:00"
    # 1.5 hours = 01:30
    assert hour_to_hm(1.5) == "01:30"
    # 23.75 hours = 23:45
    assert hour_to_hm(23.75) == "23:45"

    # --- ghati conversions ---------------------------------------------
    print("\n[ ghati_to_gp / ghati_to_gpb samples ]")
    print("ghati_to_gp(0.0)   =", ghati_to_gp(0.0))
    print("ghati_to_gp(1.0)   =", ghati_to_gp(1.0))
    print("ghati_to_gpb(1.0)  =", ghati_to_gpb(1.0))
    print("ghati_to_gpb(10.5) =", ghati_to_gpb(10.5))

    assert ghati_to_gp(0.0) == "00:00"
    # 1 ghati = 60 pala → "01:00"
    assert ghati_to_gp(1.0) == "01:00"
    # 1 ghati = 60*60 bipala = 3600 bipala → "01:00:00"
    assert ghati_to_gpb(1.0) == "01:00:00"

    # --- calc_shaka_year ----------------------------------------------
    print("\n[ calc_shaka_year samples ]")
    d1 = date(2025, 1, 1)   # before or on boundary -> year - 79
    d2 = date(2025, 4, 1)   # after boundary -> year - 78

    print("calc_shaka_year(2025-01-01) =", calc_shaka_year(d1))
    print("calc_shaka_year(2025-04-01) =", calc_shaka_year(d2))

    assert calc_shaka_year(d1) == 2025 - 79  # 1946
    assert calc_shaka_year(d2) == 2025 - 78  # 1947

    print("\nAll core_functions self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()
