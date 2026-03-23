# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping

from bheshajpatro.engines.ketaki.core.constants import madhyama_gati

__all__ = ["TARA_GRAHAS", "compute_panchatara_gati"]

TARA_GRAHAS = ("mangal", "budha", "guru", "shukra", "shani")


def _manda_component(mandakantar: Mapping[str, float]) -> dict[str, float]:
    """
    manda-phala contribution to gati (deg/day)
    """
    div = {
        "mangal": 3.0,
        "budha": 2.0,
        "guru": 20.0,
        "shukra": 60.0,
        "shani": 50.0,
    }
    budha_mul = 5.0

    out: dict[str, float] = {}

    for g in TARA_GRAHAS:
        mk = mandakantar.get(g)
        if mk is None:
            continue

        mins = (mk / div[g]) * budha_mul if g == "budha" else (mk / div[g])
        out[g] = mins / 60.0

    return out


def _shighra_component(shighrakantar: Mapping[str, float]) -> dict[str, float]:
    """
    shighra-phala contribution to gati (deg/day)
    """
    div = {
        "mangal": 4.0,
        "budha": 6.0,
        "guru": 2.0,
        "shukra": 3.0,
        "shani": 2.0,
    }
    budha_mul = 10.0

    out: dict[str, float] = {}

    for g in TARA_GRAHAS:
        sk = shighrakantar.get(g)
        if sk is None:
            continue

        mins = (sk + (sk / 9.0)) / div[g]

        if g == "budha":
            mins *= budha_mul

        out[g] = mins / 60.0

    return out


def compute_panchatara_gati(
    *,
    mandakantar: Mapping[str, float],
    shighrakantar: Mapping[str, float],
    surya_gati: float,
) -> dict[str, dict[str, float]]:
    """
    Combine manda + shighra corrections into final tara gati.
    """
    base = {g: float(madhyama_gati[g]) for g in TARA_GRAHAS}

    gm = _manda_component(mandakantar)
    mandagati = {g: base[g] - gm.get(g, 0.0) for g in TARA_GRAHAS}

    gs = _shighra_component(shighrakantar)

    shigr: dict[str, float] = {}

    for g in TARA_GRAHAS:
        if g in ("budha", "shukra"):
            shigr[g] = float(surya_gati) + gs.get(g, 0.0)
        else:
            shigr[g] = mandagati[g] + gs.get(g, 0.0)

    return {
        "gatimandaphala": gm,
        "mandagati": mandagati,
        "gatishighraphala": gs,
        "shighragati": shigr,
    }