# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.core.core_functions import calc_shadvalpa, norm_360
from bheshajpatro.engines.ketaki.core.anglefunc.beejas import calc_beeja
from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import calc_phalanka
from bheshajpatro.engines.ketaki.core.constants import madhyama_gati
from bheshajpatro.engines.ketaki.core.mandafunc.madhyamas import calc_madhyama
from bheshajpatro.engines.ketaki.core.mandafunc.mandakarnas import (
    mandakarna_map,
)
from bheshajpatro.engines.ketaki.core.mandafunc.mandakendras import (
    calc_mandakendra,
)
from bheshajpatro.engines.ketaki.core.mandafunc.mandaphalas import (
    mandaphala_map,
)
from bheshajpatro.engines.ketaki.core.mandafunc.mandochas import calc_mandocha

__all__ = ["compute_manda_block"]

GRAHAS_MANDA = ("surya", "mangal", "budha", "guru", "shukra", "shani", "rahu")
MANDA_CORE_GRAHAS = ("surya", "mangal", "budha", "guru", "shukra", "shani")


def _suryagati_from_sv(sv_surya: float) -> float:
    ph = calc_phalanka("suryagati", "surya", sv_surya)
    return float(ph) / 60.0


def _calc_mandagati(
    *,
    gamyantar_map: Mapping[str, float],
) -> dict[str, float]:
    divisors = {
        "mangal": 3.0,
        "budha": 2.0,
        "guru": 20.0,
        "shukra": 40.0,
        "shani": 50.0,
    }
    out: dict[str, float] = {}

    for g, gy in gamyantar_map.items():
        div = divisors[g]
        minutes = abs(float(gy)) / div
        if g == "budha":
            minutes *= 5.0
        corr = minutes / 60.0
        sign = -1.0 if gy > 0.0 else 1.0
        out[g] = float(madhyama_gati[g]) + sign * corr

    return out


def _calc_rahu_block(rahu_madhyama: float) -> dict[str, float]:
    r = norm_360(float(rahu_madhyama))
    k = norm_360(r + 180.0)
    g = -float(madhyama_gati["rahu"])
    return {
        "rahu_spashta": r,
        "ketu_spashta": k,
        "rahu_gati": g,
        "ketu_gati": g,
    }


def compute_manda_block(
    *,
    ahargana: float,
    chakra_cnt: int,
    shaka_year: int,
) -> dict[str, Any]:
    grahas_all = GRAHAS_MANDA
    grahas_core = MANDA_CORE_GRAHAS

    beeja_map = calc_beeja(shaka_year)

    madhyama = calc_madhyama(
        grahas_all,
        ahargana=ahargana,
        chakra_count=chakra_cnt,
        beeja_map=beeja_map,
    )

    mandocha = calc_mandocha(
        grahas_core,
        ahargana=ahargana,
        chakra_count=chakra_cnt,
    )

    mandakendra = calc_mandakendra(
        madhyama=madhyama,
        mandocha=mandocha,
        grahas=grahas_core,
    )

    shadvalpa: dict[str, float] = {
        g: calc_shadvalpa(mandakendra[g]) for g in grahas_core
    }

    mp_info = mandaphala_map(grahas_core, sv_map=shadvalpa)
    mandaphala_deg: dict[str, float] = {
        g: mp_info[g]["value_deg"] for g in grahas_core
    }
    mandakantar: dict[str, float] = {
        g: mp_info[g]["gamyantar"] for g in grahas_core
    }

    mandaspashta: dict[str, float] = {}
    for g in grahas_core:
        mm = float(madhyama[g])
        ph = float(mandaphala_deg[g])
        mk = float(mandakendra[g])

        if mk <= 180.0:
            val = mm - ph
        else:
            val = mm + ph

        mandaspashta[g] = norm_360(val)

    manda_subset = {
        g: mandakantar[g]
        for g in ("mangal", "budha", "guru", "shukra", "shani")
    }
    manda_gati_core = _calc_mandagati(gamyantar_map=manda_subset)

    rk = _calc_rahu_block(madhyama["rahu"])

    surya_sv = shadvalpa["surya"]
    surya_gati = _suryagati_from_sv(surya_sv)

    mandagati: dict[str, float] = {
        "surya": float(surya_gati),
        "mangal": float(manda_gati_core["mangal"]),
        "budha": float(manda_gati_core["budha"]),
        "guru": float(manda_gati_core["guru"]),
        "shukra": float(manda_gati_core["shukra"]),
        "shani": float(manda_gati_core["shani"]),
        "rahu": float(rk["rahu_gati"]),
        "ketu": float(rk["ketu_gati"]),
    }

    mandakarna_info = mandakarna_map(sv_map=shadvalpa)
    mandakarna: dict[str, float] = {
        g: mandakarna_info[g]["value_deg"] for g in mandakarna_info
    }

    return {
        "madhyama": madhyama,
        "mandocha": mandocha,
        "mandakendra": mandakendra,
        "shadvalpa": shadvalpa,
        "mandaphala_deg": mandaphala_deg,
        "mandakantar": mandakantar,
        "mandaspashta": {
            **mandaspashta,
            "rahu": rk["rahu_spashta"],
            "ketu": rk["ketu_spashta"],
        },
        "mandagati": mandagati,
        "mandakarna": mandakarna,
    }