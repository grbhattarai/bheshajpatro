# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Engine-agnostic daily Panchanga builder.
#
# Input:
#   session dict from a daily engine (e.g. drik calc_pday.run)
#
# Output:
#   session["astro"]["panchanga_result"]

from __future__ import annotations

# =============================================================================
# DEV OVERRIDE (REMOVE AFTER TESTING)
# -----------------------------------------------------------------------------
# Allows direct execution:
#     python pbuilder/pa2_daypanchanga.py
# =============================================================================
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    PACKAGE_PARENT = Path(__file__).resolve().parents[2]
    if str(PACKAGE_PARENT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_PARENT))
# =============================================================================

from datetime import date as _date, datetime, timezone
from typing import Any, Dict, List, Mapping

from zoneinfo import ZoneInfo

from bheshajpatro.core.core_functions import ghati_to_gp, hour_to_hm, norm_360
from bheshajpatro.data.mapnames import (
    get_emonth_name,
    get_karana_name,
    get_nakshatra_name,
    get_nmonth_name,
    get_nyoga_name,
    get_rashi_name,
    get_tithi_name,
    get_weekday_name,
)

__all__ = [
    "rashi_index_from_deg",
    "ghati_to_hours",
    "compute_tithi",
    "compute_nakshatra",
    "compute_yoga",
    "compute_dinamana",
    "compute_karana",
    "calc_panchanga",
    "run",
]

DAY_GHATI_BETWEEN_SUNRISES = 60.0


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def ghati_to_hours(ghati: float) -> float:
    """Convert ghati → decimal hours. 1 ghati = 0.4 hours."""
    return float(ghati) * 0.4


def rashi_index_from_deg(deg: float | int) -> int:
    """1-based rashi index from longitude in degrees."""
    return 1 + int((float(deg) % 360.0) // 30.0)


def _strict_get(d: Mapping[str, Any], *path: str) -> Any:
    """Strict nested dict getter with clear errors."""
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError("missing key path: " + " -> ".join(path))
        cur = cur[k]
    return cur


def _blank_if_none(s: str | None) -> str:
    return s or ""


def _compute_bs_year(date_ce: _date) -> int:
    """
    Bikram Samvat year from Gregorian date.
    """
    if date_ce.month > 4 or (date_ce.month == 4 and date_ce.day >= 14):
        return date_ce.year + 57
    return date_ce.year + 56


def _compute_dst_offset_hours(date_ce: _date, location: Mapping[str, Any]) -> float:
    """
    Compute DST offset in hours from tz_name and std_meridian.
    """
    tz_name = location.get("tz_name")
    std_mer = location.get("std_meridian")

    if not tz_name or std_mer is None:
        return 0.0

    try:
        tz = ZoneInfo(str(tz_name))
    except Exception:
        return 0.0

    dt_utc = datetime(date_ce.year, date_ce.month, date_ce.day, 12, 0, 0, tzinfo=timezone.utc)
    offset = tz.utcoffset(dt_utc)
    if offset is None:
        return 0.0

    actual_hours = offset.total_seconds() / 3600.0
    standard_hours = float(std_mer) / 15.0
    return actual_hours - standard_hours


def _hour_to_hm_24plus(hours: float) -> str:
    """
    Convert decimal hours -> HH:MM without mod-24 wrap.
    """
    total_minutes = int(round(float(hours) * 60.0))
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


# ---------------------------------------------------------------------------
# Pure Panchanga math
# ---------------------------------------------------------------------------

def compute_tithi(
    surya_deg: float,
    chandra_deg: float,
    surya_speed: float,
    chandra_speed: float,
) -> Dict[str, float]:
    TITHI_SIZE = 12.0

    ch_span = chandra_deg + 360.0 if chandra_deg < surya_deg else chandra_deg
    graha_antar = ch_span - surya_deg
    gati_antar = chandra_speed - surya_speed

    gata_tithi = int(graha_antar // TITHI_SIZE)
    today_tithi = gata_tithi + 1

    tithi_bhuktamsha = graha_antar % TITHI_SIZE
    tithi_bhogya = TITHI_SIZE - tithi_bhuktamsha

    if abs(gati_antar) < 1e-9:
        tithi_bhogya_ghati = 0.0
    else:
        tithi_bhogya_ghati = (tithi_bhogya * 60.0) / gati_antar

    return {
        "index": float(today_tithi),
        "gata_tithi": float(gata_tithi),
        "bhuktamsha_deg": float(tithi_bhuktamsha),
        "bhogya_deg": float(tithi_bhogya),
        "bhogya_ghati": float(tithi_bhogya_ghati),
    }


def compute_nakshatra(body_deg: float, body_speed: float) -> Dict[str, float]:
    N = 360.0 / 27.0

    gata_naks = int(body_deg // N)
    today_naks = gata_naks + 1

    naks_bhuktamsha = body_deg % N
    naks_bhogya = N - naks_bhuktamsha

    if abs(body_speed) < 1e-9:
        naks_bhogya_ghati = 0.0
    else:
        naks_bhogya_ghati = (naks_bhogya * 60.0) / body_speed

    return {
        "index": float(today_naks),
        "bhuktamsha_deg": float(naks_bhuktamsha),
        "bhogya_deg": float(naks_bhogya),
        "bhogya_ghati": float(naks_bhogya_ghati),
    }


def compute_yoga(
    surya_deg: float,
    chandra_deg: float,
    surya_speed: float,
    chandra_speed: float,
) -> Dict[str, float]:
    N = 360.0 / 27.0

    yoga_deg = (surya_deg + chandra_deg) % 360.0
    yoga_speed = surya_speed + chandra_speed

    gata_yoga = int(yoga_deg // N)
    today_yoga = gata_yoga + 1

    yoga_bhuktamsha = yoga_deg % N
    yoga_bhogya = N - yoga_bhuktamsha

    if abs(yoga_speed) < 1e-9:
        yoga_bhogya_ghati = 0.0
    else:
        yoga_bhogya_ghati = (yoga_bhogya * 60.0) / yoga_speed

    return {
        "index": float(today_yoga),
        "bhuktamsha_deg": float(yoga_bhuktamsha),
        "bhogya_deg": float(yoga_bhogya),
        "bhogya_ghati": float(yoga_bhogya_ghati),
    }


def compute_dinamana(sunrise_hours: float, sunset_hours: float) -> Dict[str, float]:
    delta_hours = (float(sunset_hours) - float(sunrise_hours)) % 24.0
    dinamana_ghati = 2.5 * delta_hours
    return {
        "delta_hours": float(delta_hours),
        "dinamana_ghati": float(dinamana_ghati),
    }


def _karana_index_from_slot(slot: int) -> int:
    """
    Map 1-based karana slot (1..60, each 6° of Sun-Moon separation)
    to karana number 1..11.
    """
    if slot <= 56:
        return ((slot - 1) % 7) + 1
    return 7 + (slot - 56)


def compute_karana(
    surya_deg: float,
    chandra_deg: float,
    surya_speed: float,
    chandra_speed: float,
) -> Dict[str, float]:
    KARANA_SIZE = 6.0

    ch_span = chandra_deg + 360.0 if chandra_deg < surya_deg else chandra_deg
    graha_antar = ch_span - surya_deg
    gati_antar = chandra_speed - surya_speed

    slot_0_based = int(graha_antar // KARANA_SIZE)
    slot_index = slot_0_based + 1
    karana_index = _karana_index_from_slot(slot_index)

    karana_bhuktamsha = graha_antar % KARANA_SIZE
    karana_bhogya = KARANA_SIZE - karana_bhuktamsha

    if abs(gati_antar) < 1e-9:
        karana_bhogya_ghati = 0.0
    else:
        karana_bhogya_ghati = (karana_bhogya * 60.0) / gati_antar

    return {
        "slot_index": float(slot_index),
        "karana_index": float(karana_index),
        "bhogya_ghati": float(karana_bhogya_ghati),
    }


def _segment_limb_for_day(
    *,
    first_index: int,
    first_bhogya_ghati: float,
    unit_deg: float,
    rel_speed: float,
    cycle_len: int,
    sunrise_std: float,
    dst_offset_hours: float,
    max_segments: int = 3,
) -> List[dict]:
    segments: List[dict] = []

    if abs(rel_speed) < 1e-9:
        segments.append(
            {
                "index": first_index,
                "start_hm": _hour_to_hm_24plus(sunrise_std + dst_offset_hours),
                "end_hm": None,
                "ahoratra": True,
            }
        )
        return segments

    full_ghati = (unit_deg * 60.0) / rel_speed

    if first_bhogya_ghati >= DAY_GHATI_BETWEEN_SUNRISES - 1e-6:
        segments.append(
            {
                "index": first_index,
                "start_hm": _hour_to_hm_24plus(sunrise_std + dst_offset_hours),
                "end_hm": None,
                "ahoratra": True,
            }
        )
        return segments

    remaining_gh = DAY_GHATI_BETWEEN_SUNRISES
    start_gh = 0.0
    idx = first_index

    for seg_no in range(max_segments):
        seg_len_gh = first_bhogya_ghati if seg_no == 0 else full_ghati

        if seg_len_gh >= remaining_gh - 1e-6:
            segments.append(
                {
                    "index": idx,
                    "start_hm": _hour_to_hm_24plus(
                        sunrise_std + ghati_to_hours(start_gh) + dst_offset_hours
                    ),
                    "end_hm": None,
                    "ahoratra": False,
                }
            )
            break

        end_gh = start_gh + seg_len_gh

        segments.append(
            {
                "index": idx,
                "start_hm": _hour_to_hm_24plus(
                    sunrise_std + ghati_to_hours(start_gh) + dst_offset_hours
                ),
                "end_hm": _hour_to_hm_24plus(
                    sunrise_std + ghati_to_hours(end_gh) + dst_offset_hours
                ),
                "ahoratra": False,
            }
        )

        remaining_gh -= seg_len_gh
        start_gh = end_gh
        if remaining_gh <= 1e-6:
            break

        idx = (idx % cycle_len) + 1

    return segments


# ---------------------------------------------------------------------------
# Core Panchanga builder
# ---------------------------------------------------------------------------

def calc_panchanga(session: dict[str, Any]) -> dict[str, Any]:
    ctx = session.get("context", {})
    dt_iso = _strict_get(ctx, "date")
    date_ce: _date = datetime.fromisoformat(str(dt_iso)).date()

    greg_weekday = date_ce.weekday()
    day_nbr = float(greg_weekday)
    day_name = get_weekday_name(greg_weekday + 1, "en")

    shaka_year = date_ce.year - 78
    bs_year = _compute_bs_year(date_ce)

    location = ctx.get("location", {})
    dst_offset_hours = _compute_dst_offset_hours(date_ce, location)

    astro = _strict_get(session, "astro")

    if "suryodaya_spashta" in astro:
        spashta = astro["suryodaya_spashta"]
    else:
        spashta = _strict_get(astro, "graha_spashta")

    if "suryodaya_gati" in astro:
        gati = astro["suryodaya_gati"]
    else:
        gati = _strict_get(astro, "graha_gati")

    surya_deg = float(_strict_get(spashta, "surya"))
    chandra_deg = float(_strict_get(spashta, "chandra"))
    surya_speed = float(_strict_get(gati, "surya"))
    chandra_speed = float(_strict_get(gati, "chandra"))

    sunrise_std = float(_strict_get(astro, "sunrise_hours"))
    sunset_std = float(_strict_get(astro, "sunset_hours"))

    tithi_info = compute_tithi(surya_deg, chandra_deg, surya_speed, chandra_speed)
    chandra_naks_info = compute_nakshatra(chandra_deg, chandra_speed)
    surya_naks_info = compute_nakshatra(surya_deg, surya_speed)
    yoga_info = compute_yoga(surya_deg, chandra_deg, surya_speed, chandra_speed)
    dinamana_info = compute_dinamana(sunrise_std, sunset_std)
    karana_info = compute_karana(surya_deg, chandra_deg, surya_speed, chandra_speed)

    tithi1_idx = int(tithi_info["index"])
    nakshatra1_idx = int(chandra_naks_info["index"])
    yoga1_idx = int(yoga_info["index"])
    surya_nakshatra1_idx = int(surya_naks_info["index"])

    tithi_bhogya_ghati = tithi_info["bhogya_ghati"]
    naks_bhogya_ghati = chandra_naks_info["bhogya_ghati"]
    yoga_bhogya_ghati = yoga_info["bhogya_ghati"]
    surya_naks_bhogya_ghati = surya_naks_info["bhogya_ghati"]

    dinamana_hours = dinamana_info["delta_hours"]
    dinamana_ghati = dinamana_info["dinamana_ghati"]

    karana1_idx = int(karana_info["karana_index"])
    karana_bhogya_ghati = karana_info["bhogya_ghati"]

    sun_rashi1_idx = rashi_index_from_deg(surya_deg)
    moon_rashi1_idx = rashi_index_from_deg(chandra_deg)

    # Your NMONTH is solar month based on Surya longitude
    nmonth = sun_rashi1_idx

    gati_antar = chandra_speed - surya_speed
    yoga_speed = surya_speed + chandra_speed

    tithi_segments = _segment_limb_for_day(
        first_index=tithi1_idx,
        first_bhogya_ghati=tithi_bhogya_ghati,
        unit_deg=12.0,
        rel_speed=gati_antar,
        cycle_len=30,
        sunrise_std=sunrise_std,
        dst_offset_hours=dst_offset_hours,
        max_segments=3,
    )

    chandra_naks_segments = _segment_limb_for_day(
        first_index=nakshatra1_idx,
        first_bhogya_ghati=naks_bhogya_ghati,
        unit_deg=360.0 / 27.0,
        rel_speed=chandra_speed,
        cycle_len=27,
        sunrise_std=sunrise_std,
        dst_offset_hours=dst_offset_hours,
        max_segments=3,
    )

    surya_naks_segments = _segment_limb_for_day(
        first_index=surya_nakshatra1_idx,
        first_bhogya_ghati=surya_naks_bhogya_ghati,
        unit_deg=360.0 / 27.0,
        rel_speed=surya_speed,
        cycle_len=27,
        sunrise_std=sunrise_std,
        dst_offset_hours=dst_offset_hours,
        max_segments=2,
    )

    yoga_segments = _segment_limb_for_day(
        first_index=yoga1_idx,
        first_bhogya_ghati=yoga_bhogya_ghati,
        unit_deg=360.0 / 27.0,
        rel_speed=yoga_speed,
        cycle_len=27,
        sunrise_std=sunrise_std,
        dst_offset_hours=dst_offset_hours,
        max_segments=3,
    )

    karana_segments = _segment_limb_for_day(
        first_index=int(karana_info["slot_index"]),
        first_bhogya_ghati=karana_bhogya_ghati,
        unit_deg=6.0,
        rel_speed=gati_antar,
        cycle_len=60,
        sunrise_std=sunrise_std,
        dst_offset_hours=dst_offset_hours,
        max_segments=4,
    )

    t0 = tithi_segments[0]
    n0 = chandra_naks_segments[0]
    y0 = yoga_segments[0]
    s0 = surya_naks_segments[0]

    if t0["ahoratra"]:
        tithi1_hm = "ahoratra"
        tithi1_gp = "ahoratra"
    elif t0["end_hm"] is None:
        tithi1_hm = None
        tithi1_gp = None
    else:
        tithi1_hm = t0["end_hm"]
        tithi1_gp = ghati_to_gp(tithi_bhogya_ghati)

    if n0["ahoratra"]:
        nakshatra1_hm = "ahoratra"
        nakshatra1_gp = "ahoratra"
    elif n0["end_hm"] is None:
        nakshatra1_hm = None
        nakshatra1_gp = None
    else:
        nakshatra1_hm = n0["end_hm"]
        nakshatra1_gp = ghati_to_gp(naks_bhogya_ghati)

    if s0["ahoratra"]:
        surya_nakshatra1_hm = "ahoratra"
        surya_nakshatra1_gp = "ahoratra"
    elif s0["end_hm"] is None:
        surya_nakshatra1_hm = None
        surya_nakshatra1_gp = None
    else:
        surya_nakshatra1_hm = s0["end_hm"]
        surya_nakshatra1_gp = ghati_to_gp(surya_naks_bhogya_ghati)

    if y0["ahoratra"]:
        yoga1_hm = "ahoratra"
        yoga1_gp = "ahoratra"
    elif y0["end_hm"] is None:
        yoga1_hm = None
        yoga1_gp = None
    else:
        yoga1_hm = y0["end_hm"]
        yoga1_gp = ghati_to_gp(yoga_bhogya_ghati)

    tithi2_idx = tithi3_idx = None
    tithi2_hm = tithi3_hm = None
    if len(tithi_segments) >= 2:
        t1 = tithi_segments[1]
        tithi2_idx = int(t1["index"])
        tithi2_hm = t1["end_hm"]
    if len(tithi_segments) >= 3:
        t2 = tithi_segments[2]
        tithi3_idx = int(t2["index"])
        tithi3_hm = t2["end_hm"]

    nakshatra2_idx = nakshatra3_idx = None
    nakshatra2_hm = nakshatra3_hm = None
    if len(chandra_naks_segments) >= 2:
        n1 = chandra_naks_segments[1]
        nakshatra2_idx = int(n1["index"])
        nakshatra2_hm = n1["end_hm"]
    if len(chandra_naks_segments) >= 3:
        n2 = chandra_naks_segments[2]
        nakshatra3_idx = int(n2["index"])
        nakshatra3_hm = n2["end_hm"]

    yoga2_idx = yoga3_idx = None
    yoga2_hm = yoga3_hm = None
    if len(yoga_segments) >= 2:
        y1 = yoga_segments[1]
        yoga2_idx = int(y1["index"])
        yoga2_hm = y1["end_hm"]
    if len(yoga_segments) >= 3:
        y2 = yoga_segments[2]
        yoga3_idx = int(y2["index"])
        yoga3_hm = y2["end_hm"]

    surya_nakshatra2_idx = None
    surya_nakshatra2_hm = None
    if len(surya_naks_segments) >= 2:
        s1 = surya_naks_segments[1]
        surya_nakshatra2_idx = int(s1["index"])
        surya_nakshatra2_hm = s1["end_hm"]

    karana1_hm = karana2_hm = karana3_hm = karana4_hm = None
    karana2_idx = karana3_idx = karana4_idx = None

    if len(karana_segments) >= 1:
        k0 = karana_segments[0]
        karana1_idx = _karana_index_from_slot(int(k0["index"]))
        karana1_hm = k0["end_hm"]
    if len(karana_segments) >= 2:
        k1 = karana_segments[1]
        karana2_idx = _karana_index_from_slot(int(k1["index"]))
        karana2_hm = k1["end_hm"]
    if len(karana_segments) >= 3:
        k2 = karana_segments[2]
        karana3_idx = _karana_index_from_slot(int(k2["index"]))
        karana3_hm = k2["end_hm"]
    if len(karana_segments) >= 4:
        k3 = karana_segments[3]
        karana4_idx = _karana_index_from_slot(int(k3["index"]))
        karana4_hm = k3["end_hm"]

    moon_rashi2_idx = None
    moon_rashi1_hm = None

    if abs(chandra_speed) > 1e-9:
        chandra_deg_mod = chandra_deg % 360.0
        current_rashi_start_deg = (moon_rashi1_idx - 1) * 30.0
        next_boundary_deg = current_rashi_start_deg + 30.0

        remaining_deg_rashi = next_boundary_deg - chandra_deg_mod
        if remaining_deg_rashi < 0:
            remaining_deg_rashi += 30.0

        ghati_to_next_rashi = (remaining_deg_rashi * 60.0) / chandra_speed

        if ghati_to_next_rashi < DAY_GHATI_BETWEEN_SUNRISES - 1e-6:
            moon_rashi1_hm = _hour_to_hm_24plus(
                sunrise_std + ghati_to_hours(ghati_to_next_rashi) + dst_offset_hours
            )
            moon_rashi2_idx = (moon_rashi1_idx % 12) + 1

    dinamana_hm = hour_to_hm(dinamana_hours)
    dinamana_gp = ghati_to_gp(dinamana_ghati)

    sunrise_hm = hour_to_hm(sunrise_std + dst_offset_hours)
    sunset_hm = hour_to_hm(sunset_std + dst_offset_hours)

    surya_deg_mod = surya_deg % 30.0
    sun_day = 1 + int(surya_deg_mod // max(surya_speed, 1e-9))

    emonth = date_ce.month
    emonth_name = get_emonth_name(emonth, "en")
    nmonth_name = get_nmonth_name(nmonth, "en")

    sun_rashi1_name = get_rashi_name(sun_rashi1_idx, "en")
    moon_rashi1_name = get_rashi_name(moon_rashi1_idx, "en")
    moon_rashi2_name = get_rashi_name(moon_rashi2_idx, "en") if moon_rashi2_idx is not None else None

    date_bs = f"{sun_day:02d}-{nmonth:02d}-{bs_year:04d}"
    paksha = "shukla" if 1 <= tithi1_idx <= 15 else "krishna"

    result: Dict[str, Any] = {
        "date_ce": date_ce.isoformat(),
        "date_bs": date_bs,
        "bs_year": bs_year,
        "shaka_year": shaka_year,
        "day_nbr": round(day_nbr, 3),
        "day_name": day_name,

        "paksha": paksha,

        "emonth": emonth,
        "emonth_name": emonth_name,
        "nmonth": nmonth,
        "nmonth_name": nmonth_name,

        "tithi1": tithi1_idx,
        "tithi1_gp": _blank_if_none(tithi1_gp),
        "tithi1_hm": _blank_if_none(tithi1_hm),
        "tithi1_name": get_tithi_name(tithi1_idx, "en"),

        "nakshatra1": nakshatra1_idx,
        "nakshatra1_gp": _blank_if_none(nakshatra1_gp),
        "nakshatra1_hm": _blank_if_none(nakshatra1_hm),
        "nakshatra1_name": get_nakshatra_name(nakshatra1_idx, "en"),

        "surya_nakshatra1": surya_nakshatra1_idx,
        "surya_nakshatra1_gp": _blank_if_none(surya_nakshatra1_gp),
        "surya_nakshatra1_hm": _blank_if_none(surya_nakshatra1_hm),
        "surya_nakshatra1_name": get_nakshatra_name(surya_nakshatra1_idx, "en"),

        "yoga1": yoga1_idx,
        "yoga1_gp": _blank_if_none(yoga1_gp),
        "yoga1_hm": _blank_if_none(yoga1_hm),
        "yoga1_name": get_nyoga_name(yoga1_idx, "en"),

        "karana1": karana1_idx,
        "karana1_hm": _blank_if_none(karana1_hm),
        "karana1_name": get_karana_name(karana1_idx, "en"),

        "sun_degree": round(norm_360(surya_deg), 3),
        "sun_rashi1": sun_rashi1_idx,
        "sun_rashi1_name": sun_rashi1_name,

        "moon_degree": round(norm_360(chandra_deg), 3),
        "moon_rashi1": moon_rashi1_idx,
        "moon_rashi1_name": moon_rashi1_name,
        "moon_rashi1_hm": _blank_if_none(moon_rashi1_hm),

        "dinamana_hm": dinamana_hm,
        "dinamana_gp": dinamana_gp,
        "dinamana_dec": round(dinamana_ghati, 3),

        "sunrise_hm": sunrise_hm,
        "sunset_hm": sunset_hm,
        "sunrise_dec": round(sunrise_std, 3),
        "sunset_dec": round(sunset_std, 3),
        "dst_hours": round(dst_offset_hours, 3),

        "sun_day": int(sun_day),
    }

    if moon_rashi2_idx is not None:
        result["moon_rashi2"] = moon_rashi2_idx
        result["moon_rashi2_name"] = moon_rashi2_name

    if tithi2_idx is not None:
        result["tithi2"] = tithi2_idx
        result["tithi2_hm"] = _blank_if_none(tithi2_hm)
        result["tithi2_name"] = get_tithi_name(tithi2_idx, "en")
    if tithi3_idx is not None:
        result["tithi3"] = tithi3_idx
        result["tithi3_hm"] = _blank_if_none(tithi3_hm)
        result["tithi3_name"] = get_tithi_name(tithi3_idx, "en")

    if nakshatra2_idx is not None:
        result["nakshatra2"] = nakshatra2_idx
        result["nakshatra2_hm"] = _blank_if_none(nakshatra2_hm)
        result["nakshatra2_name"] = get_nakshatra_name(nakshatra2_idx, "en")
    if nakshatra3_idx is not None:
        result["nakshatra3"] = nakshatra3_idx
        result["nakshatra3_hm"] = _blank_if_none(nakshatra3_hm)
        result["nakshatra3_name"] = get_nakshatra_name(nakshatra3_idx, "en")

    if surya_nakshatra2_idx is not None:
        result["surya_nakshatra2"] = surya_nakshatra2_idx
        result["surya_nakshatra2_hm"] = _blank_if_none(surya_nakshatra2_hm)
        result["surya_nakshatra2_name"] = get_nakshatra_name(surya_nakshatra2_idx, "en")

    if yoga2_idx is not None:
        result["yoga2"] = yoga2_idx
        result["yoga2_hm"] = _blank_if_none(yoga2_hm)
        result["yoga2_name"] = get_nyoga_name(yoga2_idx, "en")
    if yoga3_idx is not None:
        result["yoga3"] = yoga3_idx
        result["yoga3_hm"] = _blank_if_none(yoga3_hm)
        result["yoga3_name"] = get_nyoga_name(yoga3_idx, "en")

    if karana2_idx is not None:
        result["karana2"] = karana2_idx
        result["karana2_hm"] = _blank_if_none(karana2_hm)
        result["karana2_name"] = get_karana_name(karana2_idx, "en")
    if karana3_idx is not None:
        result["karana3"] = karana3_idx
        result["karana3_hm"] = _blank_if_none(karana3_hm)
        result["karana3_name"] = get_karana_name(karana3_idx, "en")
    if karana4_idx is not None:
        result["karana4"] = karana4_idx
        result["karana4_hm"] = _blank_if_none(karana4_hm)
        result["karana4_name"] = get_karana_name(karana4_idx, "en")

    return result


def run(session: dict[str, Any]) -> dict[str, Any]:
    """
    Attach panchanga_result under session['astro'] and return session.
    """
    result = calc_panchanga(session)
    astro = session.setdefault("astro", {})
    astro["panchanga_result"] = result
    return session


# ---------------------------------------------------------------------------
# SIMPLE SELF-TESTS
# ---------------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running pa2_daypanchanga self-tests...")

    from datetime import date as _d
    from bheshajpatro.engines.drik.grahas.calc_pday import run as drik_day_run

    d_test = _d(2025, 1, 1)
    session = drik_day_run(
        d_test,
        latitude=27.7172,
        longitude=85.3240,
        std_meridian=86.25,
        tz_name="Asia/Kathmandu",
        elevation=1300.0,
    )
    session = run(session)

    result = session["astro"]["panchanga_result"]

    print("\n[ Panchanga summary ]")
    print("date_ce        :", result["date_ce"])
    print("date_bs        :", result["date_bs"])
    print("day_name       :", result["day_name"])
    print("emonth_name    :", result["emonth_name"])
    print("nmonth_name    :", result["nmonth_name"])
    print("sunrise_hm     :", result["sunrise_hm"])
    print("sunset_hm      :", result["sunset_hm"])
    print("tithi1         :", result["tithi1"], result["tithi1_name"], result["tithi1_hm"])
    print("nakshatra1     :", result["nakshatra1"], result["nakshatra1_name"], result["nakshatra1_hm"])
    print("yoga1          :", result["yoga1"], result["yoga1_name"], result["yoga1_hm"])
    print("karana1        :", result["karana1"], result["karana1_name"], result["karana1_hm"])
    print("sun_rashi1     :", result["sun_rashi1"], result["sun_rashi1_name"])
    print("moon_rashi1    :", result["moon_rashi1"], result["moon_rashi1_name"])
    print("dinamana_hm    :", result["dinamana_hm"])
    print("sun_degree     :", result["sun_degree"])
    print("moon_degree    :", result["moon_degree"])

    assert result["date_ce"] == "2025-01-01"
    assert result["emonth"] == 1
    assert result["emonth_name"] == "January"
    assert result["nmonth"] == result["sun_rashi1"]
    assert 1 <= result["tithi1"] <= 30
    assert 1 <= result["nakshatra1"] <= 27
    assert 1 <= result["yoga1"] <= 27
    assert 1 <= result["karana1"] <= 11
    assert 1 <= result["sun_rashi1"] <= 12
    assert 1 <= result["moon_rashi1"] <= 12

    print("\nAll daypanchanga self-tests passed.")


if __name__ == "__main__":
    _run_self_tests()