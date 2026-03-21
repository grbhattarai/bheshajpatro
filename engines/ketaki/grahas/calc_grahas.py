# bheshajpatro/ketaki/grahas/calc_grahas.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, datetime, timezone, timedelta
from typing import Dict

from bheshajpatro.engines.ketaki.core.anglefunc.ahargana import (
    compute_ahargana,
)
from bheshajpatro.engines.ketaki.grahas.full_chain import compute_ketaki_daily
from bheshajpatro.engines.ketaki.grahas.suryodayas import (
    ayanamsha,
    surya_sayana,
    surya_kranti,
    chara,
    belantara,
    deshantara,
    local_sunrise,
    std_sunrise,
    chalana,
    sunrise_adjust,
)

from swisseph import julday as _julday

__all__ = [
    "DailyGrahasKetakiResult",
    "compute_daily_grahas_ketaki",
]

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


def _fixed_tz(std_meridian_deg: float) -> timezone:
    return timezone(timedelta(hours=std_meridian_deg / 15.0))


def _dt_to_jd(dt: datetime) -> float:
    dt_utc = dt.astimezone(timezone.utc)
    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )
    return float(_julday(dt_utc.year, dt_utc.month, dt_utc.day, hour))


@dataclass(frozen=True)
class DailyGrahasKetakiResult:
    date: _date
    latitude_deg: float
    longitude_deg: float
    standard_meridian_deg: float

    sunrise_local: datetime
    sunset_local: datetime

    jd_6am_local: float
    jd_sunrise_local: float

    graha_spashta: Dict[str, float]      # nirayana @ 6am
    suryodayaspashta: Dict[str, float]   # nirayana @ sunrise
    graha_gati: Dict[str, float]         # ketaki gati @ 6am


def compute_daily_grahas_ketaki(
    d: _date,
    *,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
) -> DailyGrahasKetakiResult:
    # 1) ahargana + ketaki daily core
    ah = compute_ahargana(
        place={
            "latitude": latitude_deg,
            "longitude": longitude_deg,
            "std_meridian": standard_meridian_deg,
        },
        for_date=d,
    )

    daily = compute_ketaki_daily(
        ahargana=ah["ahargana_ujjain"],
        chakra_cnt=ah["chakra_cnt"],
        shaka_year=ah["shaka_year"],
    )

    graha_sp = daily["graha_spashta"]
    graha_gati = daily["graha_gati"]

    # 2) 6am local datetime
    tz = _fixed_tz(standard_meridian_deg)
    six_am = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=tz)
    jd_6am = _dt_to_jd(six_am)

    # 3) sunrise computation (classical ketaki)
    aya = ayanamsha(ah["shaka_year"])
    surya_nira = graha_sp["surya"]
    sur_say = surya_sayana(surya_nira, aya)

    kranti = surya_kranti(sur_say)
    ch_hours, ch_mins = chara(latitude_deg, kranti)
    bel_hr, bel_mins = belantara(sur_say)
    desh_hr = deshantara(longitude_deg, standard_meridian_deg)

    local_sunrise_hours = local_sunrise(
        latitude=latitude_deg,
        surya_sayana_deg=sur_say,
        chara_hours=ch_hours,
        belantara_hours=bel_hr,
    )

    std_sunrise_hours = std_sunrise(
        local_sunrise_hours=local_sunrise_hours,
        deshantara_hours=desh_hr,
    )

    sr_hour = int(std_sunrise_hours)
    sr_min = int((std_sunrise_hours - sr_hour) * 60.0)
    sr_sec = int((((std_sunrise_hours - sr_hour) * 60.0) - sr_min) * 60.0)

    sunrise_local = datetime(
        d.year, d.month, d.day, sr_hour, sr_min, sr_sec, tzinfo=tz
    )
    jd_sunrise = _dt_to_jd(sunrise_local)

    # 4) dinamana + sunset (classical ketaki)
    ghatis_from_chara = ch_hours * 2.5
    adj_ghatis = ghatis_from_chara if sur_say < 180.0 else -ghatis_from_chara

    dinardha = 15.0 + adj_ghatis
    dinamana = dinardha * 2.0

    sunset_hours = std_sunrise_hours + (dinamana / 2.5)

    ss_hour = int(sunset_hours)
    ss_min = int((sunset_hours - ss_hour) * 60.0)
    ss_sec = int((((sunset_hours - ss_hour) * 60.0) - ss_min) * 60.0)

    sunset_local = datetime(
        d.year, d.month, d.day, ss_hour, ss_min, ss_sec, tzinfo=tz
    )

    # 5) suryodayaspaṣṭa for all grahas
    suryodayaspashta: Dict[str, float] = {}

    chalana_mins = chalana(
        chara_mins=ch_mins,
        belantara_mins=bel_mins,
        latitude=latitude_deg,
        surya_sayana_deg=sur_say,
    )

    for g in GRAHAS:
        spashta6 = graha_sp[g]
        gati = graha_gati[g]

        spa_sr, _raw, _adj = sunrise_adjust(
            spashta=spashta6,
            gati_per_day=gati,
            chalana_mins=chalana_mins,
        )
        suryodayaspashta[g] = spa_sr

    return DailyGrahasKetakiResult(
        date=d,
        latitude_deg=float(latitude_deg),
        longitude_deg=float(longitude_deg),
        standard_meridian_deg=float(standard_meridian_deg),
        sunrise_local=sunrise_local,
        sunset_local=sunset_local,
        jd_6am_local=jd_6am,
        jd_sunrise_local=jd_sunrise,
        graha_spashta=graha_sp,
        suryodayaspashta=suryodayaspashta,
        graha_gati=graha_gati,
    )
