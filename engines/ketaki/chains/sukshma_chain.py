# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.engines.ketaki.core.constants import madhyama_karna
from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import calc_phalanka

__all__ = ["TARA_GRAHAS", "compute_sukshma_block"]

TARA_GRAHAS = ("mangal", "budha", "guru", "shukra", "shani")

_EPS = 1e-9


def _extract_sv_from_shighrakendra(
    shighrakendra_raw: Mapping[str, Any],
) -> dict[str, float]:
    out: dict[str, float] = {}

    for g, val in shighrakendra_raw.items():
        if isinstance(val, dict):
            if "sv" in val and isinstance(val["sv"], (int, float)):
                out[g] = float(val["sv"])
            elif "skendra" in val and isinstance(val["skendra"], (int, float)):
                out[g] = float(val["skendra"])
            else:
                raise TypeError(f"cannot extract sv for {g!r} from {val!r}")
        elif isinstance(val, (int, float)):
            out[g] = float(val)
        else:
            raise TypeError(f"invalid shighrakendra[{g!r}] type {type(val)}")

    return out


def _derive_shighrakarna_from_sv(
    sv_map: Mapping[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    shighrakarna_deg: dict[str, float] = {}
    karnanka_deg: dict[str, float] = {}

    for g, sv in sv_map.items():
        if g not in madhyama_karna:
            continue

        k = float(calc_phalanka("karnanka", g, sv))
        karnanka_deg[g] = k
        shighrakarna_deg[g] = float(madhyama_karna[g]) + 100.0 - k

    return shighrakarna_deg, karnanka_deg


def compute_sukshma_block(
    *,
    shighra_block: Mapping[str, Any],
    mandakarna_deg: Mapping[str, float],
) -> dict[str, Any]:
    """
    Compute sukshma (magnitude only), karnanka, and shighrakarna.

    NOTE:
        - NO SIGN LOGIC here.
        - sukshma_deg is always positive magnitude.
    """
    sp_deg = shighra_block["shighraphala_deg"]
    skendra_raw = shighra_block["shighrakendra"]

    sv_map = _extract_sv_from_shighrakendra(skendra_raw)

    shighrakarna_deg, karnanka_deg = _derive_shighrakarna_from_sv(sv_map)

    manda_deg = {
        g: float(v)
        for g, v in mandakarna_deg.items()
        if g in ("mangal", "budha")
    }

    sukshma_deg: dict[str, float] = {}

    for g in TARA_GRAHAS:
        if g not in sp_deg:
            continue

        sp_val = float(sp_deg[g])

        if g == "mangal":
            mk = float(manda_deg["mangal"])
            shkr = float(shighrakarna_deg["mangal"])

            denom = mk + shkr - float(madhyama_karna["mangal"])
            if abs(denom) < _EPS:
                raise ZeroDivisionError("mangal sukshma denominator too small")

            suk = abs((sp_val * shkr) / denom)

        elif g == "budha":
            mk = float(manda_deg["budha"])
            divisor = float(madhyama_karna["budha"])
            suk = abs((sp_val * mk) / divisor)

        else:
            # guru, shukra, shani
            suk = abs(sp_val)

        sukshma_deg[g] = float(suk)

    return {
        "sukshma_deg": sukshma_deg,
        "shighrakarna_deg": shighrakarna_deg,
        "karnanka_deg": karnanka_deg,
        "mandakarna_deg": manda_deg,
    }