# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Compact Swiss Ephemeris wrapper (Lahiri sidereal, tropical speeds).

from __future__ import annotations

from typing import Dict, Final, Tuple

import swisseph as swe

from bheshajpatro.utils.paths import DRIK_DATA_DIR

__all__ = ["calc_graha"]

EPHEMERIS_DIR: Final = DRIK_DATA_DIR
EPHE_INITIALIZED = False
BASE_FLAGS = swe.FLG_SWIEPH  # tropical positions, ignore built-in speeds

# Canonical graha names (Hindu traditional)
CANONICAL_GRAHAS = [
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

_GRAHA_TO_IPL: Dict[str, int] = {
    "surya": swe.SUN,
    "chandra": swe.MOON,
    "mangal": swe.MARS,
    "budha": swe.MERCURY,
    "guru": swe.JUPITER,
    "shukra": swe.VENUS,
    "shani": swe.SATURN,
    "rahu": swe.MEAN_NODE,
}

GRAHA_NAME_ALIASES: Dict[str, str] = {
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
    float,  # tropical latitude
    float,  # distance (AU)
    float,  # tropical lon speed (deg/day)
    float,  # tropical lat speed (deg/day)
    float,  # distance speed (AU/day)
]


def _init_ephemeris(ephe_dir: str | None = None) -> None:
    """Initialize Swiss Ephemeris (Lahiri sidereal, data path)."""
    global EPHE_INITIALIZED
    if EPHE_INITIALIZED:
        return

    path = ephe_dir if ephe_dir is not None else str(EPHEMERIS_DIR)
    swe.set_ephe_path(path)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0.0)
    EPHE_INITIALIZED = True


def _angle_diff(deg_a: float, deg_b: float) -> float:
    """Smallest signed difference between two angles in degrees (-180, 180]."""
    diff = (deg_a - deg_b) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


def _tropical_body(jd_ut: float, ipl: int, flags: int) -> Tuple[float, float, float]:
    result, _ = swe.calc_ut(jd_ut, ipl, flags)
    lon = float(result[0])
    lat = float(result[1])
    dist = float(result[2])
    return lon, lat, dist


def _canonical_graha_name(graha: str) -> str:
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
    ephe_dir: str | None = None,
) -> GrahaResult:
    _init_ephemeris(ephe_dir)

    canonical = _canonical_graha_name(graha)

    flags = BASE_FLAGS
    if latitude is not None and longitude is not None:
        swe.set_topo(float(longitude), float(latitude), float(elevation or 0.0))
        flags |= swe.FLG_TOPOCTR

    if canonical == "ketu":
        (
            rahu_lon,
            rahu_lat,
            rahu_dist,
            rahu_lon_speed,
            rahu_lat_speed,
            rahu_dist_speed,
        ) = calc_graha(
            "rahu",
            jd_ut,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            ephe_dir=ephe_dir,
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

    ipl = _GRAHA_TO_IPL.get(canonical)
    if ipl is None:
        raise ValueError(f"unsupported canonical graha: {canonical!r}")

    dt_days = 1.0

    lon0_trop, lat0, dist0 = _tropical_body(jd_ut, ipl, flags)
    lon_plus, lat_plus, dist_plus = _tropical_body(jd_ut + dt_days, ipl, flags)
    lon_minus, lat_minus, dist_minus = _tropical_body(jd_ut - dt_days, ipl, flags)

    denom = 2.0 * dt_days
    lon_speed = _angle_diff(lon_plus, lon_minus) / denom
    lat_speed = (lat_plus - lat_minus) / denom
    dist_speed = (dist_plus - dist_minus) / denom

    ayanamsa = swe.get_ayanamsa(jd_ut)
    lon0_sidereal = (lon0_trop - ayanamsa) % 360.0

    return (
        float(lon0_sidereal),
        float(lat0),
        float(dist0),
        float(lon_speed),
        float(lat_speed),
        float(dist_speed),
    )


def _run_self_tests() -> None:
    print("Running swiss_ephem self-tests...")

    jd_ut = swe.julday(2025, 1, 1, 0.0, swe.GREG_CAL)

    surya_trad = calc_graha("surya", jd_ut)
    surya_eng = calc_graha("sun", jd_ut)
    print("\n[ Surya @ 2025-01-01 UT ]")
    print("surya (trad) =", surya_trad)
    print("surya (eng)  =", surya_eng)

    lon_s_t, lat_s_t, dist_s_t, lon_spd_s_t, *_ = surya_trad
    lon_s_e, lat_s_e, dist_s_e, lon_spd_s_e, *_ = surya_eng

    assert 0.0 <= lon_s_t < 360.0
    assert abs(lat_s_t) < 2.0
    assert dist_s_t > 0.0
    assert 0.5 < abs(lon_spd_s_t) < 1.5
    assert abs(lon_s_t - lon_s_e) < 1e-9
    assert abs(lat_s_t - lat_s_e) < 1e-9
    assert abs(dist_s_t - dist_s_e) < 1e-9

    chandra_trad = calc_graha(
        "chandra",
        jd_ut,
        latitude=27.7172,
        longitude=85.3240,
        elevation=1300.0,
    )
    chandra_eng = calc_graha(
        "moon",
        jd_ut,
        latitude=27.7172,
        longitude=85.3240,
        elevation=1300.0,
    )
    print("\n[ Chandra (topocentric) @ 2025-01-01 UT ]")
    print("chandra (trad) =", chandra_trad)
    print("chandra (eng)  =", chandra_eng)

    lon_c_t, lat_c_t, dist_c_t, lon_spd_c_t, *_ = chandra_trad
    assert 0.0 <= lon_c_t < 360.0
    assert dist_c_t > 0.0
    assert 8.0 < abs(lon_spd_c_t) < 20.0

    rahu = calc_graha("rahu", jd_ut)
    ketu = calc_graha("ketu", jd_ut)

    print("\n[ Rahu / Ketu relationship ]")
    print("rahu =", rahu)
    print("ketu =", ketu)

    lon_r, lat_r, dist_r, lon_spd_r, lat_spd_r, dist_spd_r = rahu
    lon_k, lat_k, dist_k, lon_spd_k, lat_spd_k, dist_spd_k = ketu

    expected_ketu_lon = (lon_r + 180.0) % 360.0
    assert abs((lon_k - expected_ketu_lon + 360.0) % 360.0) < 1e-6
    assert abs(lat_k + lat_r) < 1e-6
    assert abs(dist_k - dist_r) < 1e-9
    assert abs(lon_spd_k - lon_spd_r) < 1e-6
    assert abs(lat_spd_k + lat_spd_r) < 1e-6

    print("\nAll swiss_ephem self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()
