# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date, datetime, timedelta, timezone
from typing import Dict

from bheshajpatro.engines.ketaki.core.anglefunc import compute_ahargana
from bheshajpatro.engines.ketaki.chains.full_chain import compute_ketaki_daily
from bheshajpatro.engines.ketaki.grahas.suryodayas import (
    ayanamsha,
    belantara,
    chalana,
    chara,
    deshantara,
    local_sunrise,
    std_sunrise,
    sunrise_adjust,
    surya_kranti,
    surya_sayana,
)

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
    return timezone(timedelta(hours=float(std_meridian_deg) / 15.0))


def _dt_to_jd(dt: datetime) -> float:
    """
    Compute Julian Day from a timezone-aware datetime without Swiss Ephem.
    """
    dt_utc = dt.astimezone(timezone.utc)
    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day

    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )

    if m <= 2:
        y -= 1
        m += 12

    a = y // 100
    b = 2 - a + (a // 4)

    jd = (
        int(365.25 * (y + 4716))
        + int(30.6001 * (m + 1))
        + d
        + b
        - 1524.5
        + hour / 24.0
    )
    return float(jd)


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

    graha_spashta: Dict[str, float]
    suryodayaspashta: Dict[str, float]
    graha_gati: Dict[str, float]


def compute_daily_grahas_ketaki(
    d: _date,
    *,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
) -> DailyGrahasKetakiResult:
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

    tz = _fixed_tz(standard_meridian_deg)
    six_am = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=tz)
    jd_6am = _dt_to_jd(six_am)

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
        d.year,
        d.month,
        d.day,
        sr_hour,
        sr_min,
        sr_sec,
        tzinfo=tz,
    )
    jd_sunrise = _dt_to_jd(sunrise_local)

    ghatis_from_chara = ch_hours * 2.5
    adj_ghatis = ghatis_from_chara if sur_say < 180.0 else -ghatis_from_chara

    dinardha = 15.0 + adj_ghatis
    dinamana = dinardha * 2.0

    sunset_hours = std_sunrise_hours + (dinamana / 2.5)

    ss_hour = int(sunset_hours)
    ss_min = int((sunset_hours - ss_hour) * 60.0)
    ss_sec = int((((sunset_hours - ss_hour) * 60.0) - ss_min) * 60.0)

    sunset_local = datetime(
        d.year,
        d.month,
        d.day,
        ss_hour,
        ss_min,
        ss_sec,
        tzinfo=tz,
    )

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
        suryodayaspashta[g] = float(spa_sr)

    return DailyGrahasKetakiResult(
        date=d,
        latitude_deg=float(latitude_deg),
        longitude_deg=float(longitude_deg),
        standard_meridian_deg=float(standard_meridian_deg),
        sunrise_local=sunrise_local,
        sunset_local=sunset_local,
        jd_6am_local=jd_6am,
        jd_sunrise_local=jd_sunrise,
        graha_spashta={k: float(v) for k, v in graha_sp.items()},
        suryodayaspashta=suryodayaspashta,
        graha_gati={k: float(v) for k, v in graha_gati.items()},
    )