# bheshajpatro/ketaki/grahas/full_chain.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.engines.ketaki.grahas.manda_chain import compute_manda_block
from bheshajpatro.engines.ketaki.grahas.chandra_chain import (
    compute_chandra_block,
)
from bheshajpatro.engines.ketaki.grahas.shighra_chain import (
    compute_shighra_block,
)
from bheshajpatro.engines.ketaki.grahas.sukshma_chain import (
    compute_sukshma_block,
    tara_grahas,
)
from bheshajpatro.engines.ketaki.grahas.taragati_chain import (
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
    """normalize angle to [0, 360)."""
    v = float(x) % 360.0
    if v < 0.0:
        v += 360.0
    return v


def _extract_skendra_deg(
    shighrakendra_raw: Mapping[str, Any],
) -> dict[str, float]:
    """
    extract shighrakendra degrees per graha from shighra_block["shighrakendra"].

    expected per graha:
        {"graha": "mangal", "skendra": <deg>, "sv": <deg>}
    """
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
    """
    compute final tara spashta from base spashtas and unsigned sukshma.
    """
    out: dict[str, float] = {}
    surya_sp = float(mandaspashta["surya"])

    for g in tara_grahas:
        suk = float(sukshma_deg[g])
        sk = float(skendra_deg[g])

        if g in ("budha", "shukra"):
            base = surya_sp
            if sk >= 180.0:
                val = base - suk
            else:
                val = base + suk
        else:
            base = float(mandaspashta[g])
            if sk < 180.0:
                val = base - suk
            else:
                val = base + suk

        out[g] = _norm_deg(val)

    return out


def compute_ketaki_daily(
    *,
    ahargana: float,
    chakra_cnt: int,
    shaka_year: int,
) -> dict[str, Any]:
    # 1) manda chain
    manda = compute_manda_block(
        ahargana=ahargana,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )
    mandaspashta = manda["mandaspashta"]
    manda_gati = manda["mandagati"]
    mandakantar = manda["mandakantar"]
    mandakarna = manda["mandakarna"]

    # 2) chandra chain
    chandra = compute_chandra_block(
        ahargana=ahargana,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )
    chandra_spashta = chandra["chandra_spashta"]
    chandra_gati = chandra["chandra_gati"]

    # 3) shighra + sukshma + tara gati
    shighra_block = compute_shighra_block(mandaspashta=mandaspashta)

    sukshma_block = compute_sukshma_block(
        shighra_block=shighra_block,
        mandakarna_deg=mandakarna,
    )
    sukshma_deg = sukshma_block["sukshma_deg"]

    skendra_deg = _extract_skendra_deg(shighra_block["shighrakendra"])

    tara_spashta = _build_tara_spashta(
        mandaspashta=mandaspashta,
        sukshma_deg=sukshma_deg,
        skendra_deg=skendra_deg,
    )

    panchatara_gati = compute_panchatara_gati(
        mandakantar=mandakantar,
        shighrakantar=shighra_block["shighrakantar"],
        surya_gati=manda_gati["surya"],
    )
    tara_gati = panchatara_gati["shighragati"]

    shighra: dict[str, Any] = {
        "shighra_block": shighra_block,
        "sukshma_block": sukshma_block,
        "panchatara_gati": panchatara_gati,
        "tara_spashta": tara_spashta,
    }

    # 4) final graha spashta
    graha_spashta: dict[str, float] = {
        "surya": _norm_deg(mandaspashta["surya"]),
        "rahu": _norm_deg(mandaspashta["rahu"]),
        "ketu": _norm_deg(mandaspashta["ketu"]),
        "chandra": _norm_deg(chandra_spashta),
    }
    for g in tara_grahas:
        graha_spashta[g] = _norm_deg(tara_spashta[g])

    # 5) final graha gati
    graha_gati: dict[str, float] = {
        "surya": float(manda_gati["surya"]),
        "rahu": float(manda_gati["rahu"]),
        "ketu": float(manda_gati["ketu"]),
        "chandra": float(chandra_gati),
    }
    for g in tara_grahas:
        graha_gati[g] = float(tara_gati[g])

    return {
        "manda": manda,
        "chandra": chandra,
        "shighra": shighra,
        "graha_spashta": graha_spashta,
        "graha_gati": graha_gati,
    }


if __name__ == "__main__":
    from datetime import date
    from bheshajpatro.engines.ketaki.core.anglefunc.ahargana import (
        compute_ahargana,
    )

    place = {
        "city": "kathmandu",
        "latitude": 27.7,
        "longitude": 85.3,
        "std_meridian": 86.25,
        "tz": "asia/kathmandu",
    }
    for_date = date(2025, 3, 30)

    ah_info = compute_ahargana(place=place, for_date=for_date)
    ahargana_ujjain = ah_info["ahargana_ujjain"]
    ahargana_local = ah_info["ahargana"]
    chakra_cnt = ah_info["chakra_cnt"]
    shaka_year = ah_info["shaka_year"]

    daily = compute_ketaki_daily(
        ahargana=ahargana_ujjain,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )

    print("ketaki daily - kathmandu, nepal - 2025-03-30")
    print(f"ahargana_ujjain : {ahargana_ujjain:.6f}")
    print(f"ahargana_local  : {ahargana_local:.6f}")
    print(f"chakra_cnt      : {chakra_cnt}")
    print(f"shaka_year      : {shaka_year}")
    print()

    print("final graha spashta (deg):")
    for g in GRAHAS_ALL:
        v = daily["graha_spashta"].get(g)
        if v is not None:
            print(f"  {g:7s}: {v:9.6f}")

    print("\nfinal graha gati (deg/day):")
    for g in GRAHAS_ALL:
        v = daily["graha_gati"].get(g)
        if v is not None:
            print(f"  {g:7s}: {v:9.6f}")

    print()
