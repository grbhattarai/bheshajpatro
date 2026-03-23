# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.engines.ketaki.chains.manda_chain import compute_manda_block
from bheshajpatro.engines.ketaki.chains.chandra_chain import (
    compute_chandra_block,
)
from bheshajpatro.engines.ketaki.chains.shighra_chain import (
    compute_shighra_block,
)
from bheshajpatro.engines.ketaki.chains.sukshma_chain import (
    compute_sukshma_block,
    TARA_GRAHAS,
)
from bheshajpatro.engines.ketaki.chains.taragati_chain import (
    compute_panchatara_gati,
)

__all__ = ["compute_ketaki_daily"]

GRAHAS_ALL = (
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


def _norm_deg(x: float) -> float:
    v = float(x) % 360.0
    if v < 0.0:
        v += 360.0
    return v


def _extract_skendra_deg(
    shighrakendra_raw: Mapping[str, Any],
) -> dict[str, float]:
    out: dict[str, float] = {}

    for g, val in shighrakendra_raw.items():
        if isinstance(val, (int, float)):
            out[g] = float(val)

        elif isinstance(val, dict):
            if "skendra" in val and isinstance(val["skendra"], (int, float)):
                out[g] = float(val["skendra"])
            elif "sv" in val and isinstance(val["sv"], (int, float)):
                out[g] = float(val["sv"])
            else:
                raise TypeError(f"cannot extract skendra for {g!r} from {val!r}")

        else:
            raise TypeError(
                f"shighrakendra[{g!r}] must be number or dict, got {type(val)}"
            )

    return out


def _build_tara_spashta(
    *,
    mandaspashta: Mapping[str, float],
    sukshma_deg: Mapping[str, float],
    skendra_deg: Mapping[str, float],
) -> dict[str, float]:
    out: dict[str, float] = {}
    surya_sp = float(mandaspashta["surya"])

    for g in TARA_GRAHAS:
        suk = float(sukshma_deg[g])
        sk = float(skendra_deg[g])

        if g in ("budha", "shukra"):
            base = surya_sp
            val = base - suk if sk >= 180.0 else base + suk

        else:
            base = float(mandaspashta[g])
            val = base - suk if sk < 180.0 else base + suk

        out[g] = _norm_deg(val)

    return out


def compute_ketaki_daily(
    *,
    ahargana: float,
    chakra_cnt: int,
    shaka_year: int,
) -> dict[str, Any]:

    # 1) manda
    manda = compute_manda_block(
        ahargana=ahargana,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )

    mandaspashta = manda["mandaspashta"]
    manda_gati = manda["mandagati"]
    mandakantar = manda["mandakantar"]
    mandakarna = manda["mandakarna"]

    # 2) chandra
    chandra = compute_chandra_block(
        ahargana=ahargana,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )

    chandra_spashta = chandra["chandra_spashta"]
    chandra_gati = chandra["chandra_gati"]

    # 3) shighra + sukshma
    shighra_block = compute_shighra_block(mandaspashta=mandaspashta)

    sukshma_block = compute_sukshma_block(
        shighra_block=shighra_block,
        mandakarna_deg=mandakarna,
    )

    sukshma_deg = sukshma_block["sukshma_deg"]

    skendra_deg = _extract_skendra_deg(
        shighra_block["shighrakendra"]
    )

    tara_spashta = _build_tara_spashta(
        mandaspashta=mandaspashta,
        sukshma_deg=sukshma_deg,
        skendra_deg=skendra_deg,
    )

    # 4) tara gati
    panchatara_gati = compute_panchatara_gati(
        mandakantar=mandakantar,
        shighrakantar=shighra_block["shighrakantar"],
        surya_gati=manda_gati["surya"],
    )

    tara_gati = panchatara_gati["shighragati"]

    # 5) final spashta
    graha_spashta: dict[str, float] = {
        "surya": _norm_deg(mandaspashta["surya"]),
        "rahu": _norm_deg(mandaspashta["rahu"]),
        "ketu": _norm_deg(mandaspashta["ketu"]),
        "chandra": _norm_deg(chandra_spashta),
    }

    for g in TARA_GRAHAS:
        graha_spashta[g] = _norm_deg(tara_spashta[g])

    # 6) final gati
    graha_gati: dict[str, float] = {
        "surya": float(manda_gati["surya"]),
        "rahu": float(manda_gati["rahu"]),
        "ketu": float(manda_gati["ketu"]),
        "chandra": float(chandra_gati),
    }

    for g in TARA_GRAHAS:
        graha_gati[g] = float(tara_gati[g])

    return {
        "manda": manda,
        "chandra": chandra,
        "shighra": {
            "shighra_block": shighra_block,
            "sukshma_block": sukshma_block,
            "panchatara_gati": panchatara_gati,
            "tara_spashta": tara_spashta,
        },
        "graha_spashta": graha_spashta,
        "graha_gati": graha_gati,
    }