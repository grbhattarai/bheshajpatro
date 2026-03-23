# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from math import floor
from typing import Any
from collections.abc import Mapping

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.ketaki.core.upakaranas import (
    ensure_loaded,
    calc_upakarana,
    row_for,
)

__all__ = [
    "compute_chandra_block",
    "calc_chandra_spashta",
    "calc_chandra_gati",
]

_EPS = 1e-9


def _delta_forward(a2: float, a1: float) -> float:
    """forward angular delta (0..360)."""
    return (float(a2) - float(a1)) % 360.0


def _interp_upakarana(
    upa_key: int,
    ang: float,
    *,
    step: float,
) -> tuple[float, dict[str, float]]:
    a = norm_360(ang)
    lab = int(floor(a / step))
    sh = a - lab * step

    row = row_for(upa_key, lab)
    ph = row["phala"]
    ga = row["gamyantar"]

    val = ph + (sh * ga / step)

    dbg = {
        "angle": a,
        "labdhi": lab,
        "shesha": sh,
        "phala": ph,
        "gamyantar": ga,
        "value": val,
    }
    return val, dbg


def _manda_from_upa(up: Mapping[int, float]) -> tuple[float, float, float]:
    manda_vals: dict[int, float] = {}

    for key in (1, 2, 3):
        ang = norm_360(up[key])
        val, _ = _interp_upakarana(key, ang, step=6.0)
        manda_vals[key] = val

    yogaphala = manda_vals[1] + manda_vals[2] + manda_vals[3]

    madhyam = norm_360(yogaphala + up[5])
    manda_kendra = norm_360(yogaphala + up[4])

    manda_phala, _ = _interp_upakarana(4, manda_kendra, step=3.0)
    manda_spashta = norm_360(madhyam + manda_phala)

    return manda_spashta, manda_kendra, manda_phala


def _kakshabrite_from_upa(
    up: Mapping[int, float],
    mandasp: float,
) -> tuple[float, float, float]:
    chandra_kendra = norm_360(mandasp - up[6])

    kaksha_phala, _ = _interp_upakarana(5, chandra_kendra, step=6.0)
    spashta_kaksha = norm_360(mandasp + kaksha_phala)

    return spashta_kaksha, chandra_kendra, kaksha_phala


def calc_chandra_spashta(up: Mapping[int, float]) -> dict[str, Any]:
    ensure_loaded()

    mandasp, manda_k, manda_ph = _manda_from_upa(up)
    kaksha_spa, kaksha_k, kaksha_ph = _kakshabrite_from_upa(up, mandasp)

    corr_map: dict[int, float] = {
        6: up[2] * 2.0 - up[1],
        7: up[3] - up[1],
        8: manda_k - up[1],
        9: manda_k + up[1],
        10: up[5] * 2.0 - up[4],
        11: up[5] * 2.0 - (up[2] * 2.0),
    }

    adj_sum = 0.0
    corr_debug: dict[int, dict[str, float]] = {}

    for key, val in corr_map.items():
        a = norm_360(val)

        lab = int(floor(a / 30.0))
        if lab > 11:
            lab = 11

        sh = a - lab * 30.0

        row = row_for(key, lab)
        ph = row["phala"]
        ga = row["gamyantar"]

        adj = ph + (sh * ga / 30.0)

        adj_sum += adj
        corr_debug[key] = {
            "angle": a,
            "labdhi": lab,
            "shesha": sh,
            "phala": ph,
            "gamyantar": ga,
            "adj": adj,
        }

    final = norm_360(kaksha_spa + (adj_sum - (13.0 / 60.0)))

    return {
        "chandra_spashta": final,
        "mandaspashta": mandasp,
        "manda_kendra": manda_k,
        "manda_phala": manda_ph,
        "kaksha_spashta": kaksha_spa,
        "kaksha_kendra": kaksha_k,
        "kakshabrite_phala": kaksha_ph,
        "corrections": corr_debug,
    }


def calc_chandra_gati(*, ahargana: float, chakra_cnt: int) -> float:
    ensure_loaded()

    up1 = calc_upakarana(ahargana=ahargana, chakra_cnt=chakra_cnt)
    c1 = calc_chandra_spashta(up1)["chandra_spashta"]

    up2 = calc_upakarana(ahargana=ahargana + 1.0, chakra_cnt=chakra_cnt)
    c2 = calc_chandra_spashta(up2)["chandra_spashta"]

    return _delta_forward(c2, c1)


def compute_chandra_block(
    *,
    ahargana: float,
    chakra_cnt: int,
    shaka_year: int,
) -> dict[str, Any]:
    ensure_loaded()

    up = calc_upakarana(ahargana=ahargana, chakra_cnt=chakra_cnt)
    core = calc_chandra_spashta(up)
    chandra_spa = core["chandra_spashta"]

    gati = calc_chandra_gati(ahargana=ahargana, chakra_cnt=chakra_cnt)

    return {
        "chandra_spashta": float(chandra_spa),
        "chandra_gati": float(gati),
        "debug": {
            "shaka_year": int(shaka_year),
            "upakarana": {k: float(v) for k, v in up.items()},
            "core": core,
            "gati": float(gati),
        },
    }