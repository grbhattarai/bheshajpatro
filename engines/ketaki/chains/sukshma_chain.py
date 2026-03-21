# bheshajpatro/ketaki/grahas/sukshma_chain.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.engines.ketaki.core.constants import madhyama_karna
from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import calc_phalanka

__all__ = ["tara_grahas", "compute_sukshma_block"]

tara_grahas = ("mangal", "budha", "guru", "shukra", "shani")


def _extract_labdhi_map(
    shighraphala_info: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    """pull labdhi index per graha from shighraphala_info."""
    labdhi_map: dict[str, int] = {}
    for g, info in shighraphala_info.items():
        if "labdhi" not in info:
            raise KeyError(f"shighraphala_info[{g!r}] missing 'labdhi'")
        labdhi_map[g] = int(info["labdhi"])
    return labdhi_map


def _extract_shighrakendra_deg(
    shighrakendra_raw: Mapping[str, Any],
) -> dict[str, float]:
    """
    normalize shighrakendra structure to graha -> float(degrees).

    expected per graha:
        {"graha": "mangal", "skendra": <deg>, "sv": <deg>}
    """
    out: dict[str, float] = {}
    for g, val in shighrakendra_raw.items():
        if isinstance(val, (int, float)):
            out[g] = float(val)
        elif isinstance(val, dict):
            for key in ("skendra", "deg", "degree", "value", "sv", "kendra_deg"):
                v = val.get(key)
                if isinstance(v, (int, float)):
                    out[g] = float(v)
                    break
            else:
                raise TypeError(
                    f"cannot extract numeric shighrakendra for {g!r} "
                    f"from mapping {val!r}"
                )
        else:
            raise TypeError(
                f"shighrakendra[{g!r}] must be number or dict, got {type(val)}"
            )
    return out


def _extract_sv_from_shighrakendra(
    shighrakendra_raw: Mapping[str, Any],
) -> dict[str, float]:
    """
    extract sv (shadvalpa / kendra value used for phalanka interpolation)
    from shighrakendra structure.

    expected per graha:
        {"graha": "mangal", "skendra": <deg>, "sv": <deg>}
    """
    out: dict[str, float] = {}
    for g, val in shighrakendra_raw.items():
        if isinstance(val, dict):
            if "sv" in val and isinstance(val["sv"], (int, float)):
                out[g] = float(val["sv"])
            elif "skendra" in val and isinstance(val["skendra"], (int, float)):
                out[g] = float(val["skendra"])
            else:
                raise TypeError(
                    f"cannot extract sv for {g!r} from mapping {val!r}"
                )
        elif isinstance(val, (int, float)):
            out[g] = float(val)
        else:
            raise TypeError(
                f"shighrakendra[{g!r}] must be number or dict, got {type(val)}"
            )
    return out


def _derive_shighrakarna_from_sv(
    sv_map: Mapping[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """
    derive shighrakarna and karnanka for each graha:

        karnanka     = calc_phalanka("karnanka", graha, sv)
        shighrakarna = madhyama_karna[graha] + 100 - karnanka
    """
    shighrakarna_deg: dict[str, float] = {}
    karnanka_deg: dict[str, float] = {}

    for g, sv in sv_map.items():
        if g not in madhyama_karna:
            continue

        k = float(calc_phalanka("karnanka", g, sv))
        karnanka_deg[g] = k
        shighrakarna_deg[g] = float(madhyama_karna[g]) + 100.0 - k

    return shighrakarna_deg, karnanka_deg


def _apply_shighrakendra_sign(
    sukshma_raw: float,
    shighrakendra_deg: float,
) -> float:
    """
    post rule for mangal and budha:

        if shighrakendra >= 180:
            sukshmaphala := -1 * sukshmaphala
        else:
            sukshmaphala unchanged
    """
    if shighrakendra_deg >= 180.0:
        return -sukshma_raw
    return sukshma_raw


def compute_sukshma_block(
    *,
    shighra_block: Mapping[str, Any],
    mandakarna_deg: Mapping[str, float],
) -> dict[str, Any]:
    """
    compute unsigned sukshma (correction), plus karnanka and shighrakarna.

    NOTE:
        - NO SIGN LOGIC IS APPLIED HERE.
        - sukshma_deg[g] is always a +magnitude.
        - full_chain must apply sign when computing final spashta.
    """
    sp_deg = shighra_block["shighraphala_deg"]
    skendra_raw = shighra_block["shighrakendra"]

    sv_map = _extract_sv_from_shighrakendra(skendra_raw)

    shighrakarna_deg, karnanka_deg = _derive_shighrakarna_from_sv(sv_map)

    manda_deg: dict[str, float] = {
        g: float(v)
        for g, v in mandakarna_deg.items()
        if g in ("mangal", "budha")
    }

    sukshma_deg: dict[str, float] = {}

    for g in tara_grahas:
        if g not in sp_deg:
            continue

        sp_val = float(sp_deg[g])

        if g == "mangal":
            mk = float(manda_deg["mangal"])
            shkr = float(shighrakarna_deg["mangal"])

            denom = mk + shkr - float(madhyama_karna["mangal"])
            if abs(denom) < 1e-9:
                raise ZeroDivisionError("mangal sukshma denominator too small")

            purva = sp_val * shkr
            suk_raw = purva / denom
            suk = abs(float(suk_raw))

        elif g == "budha":
            mk = float(manda_deg["budha"])
            divisor = float(madhyama_karna["budha"])
            suk_raw = (sp_val * mk) / divisor
            suk = abs(float(suk_raw))

        else:
            # guru, shukra, shani → sukshma = |shighraphala|
            suk = abs(sp_val)

        sukshma_deg[g] = suk

    return {
        "sukshma_deg": sukshma_deg,
        "shighrakarna_deg": shighrakarna_deg,
        "karnanka_deg": karnanka_deg,
        "mandakarna_deg": manda_deg,
    }


if __name__ == "__main__":
    from datetime import date
    from bheshajpatro.engines.ketaki.core.anglefunc.ahargana import (
        compute_ahargana,
    )
    from bheshajpatro.engines.ketaki.grahas.manda_chain import (
        compute_manda_block,
    )
    from bheshajpatro.engines.ketaki.grahas.shighra_chain import (
        compute_shighra_block,
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
    chakra_cnt = ah_info["chakra_cnt"]
    shaka_year = ah_info["shaka_year"]

    manda = compute_manda_block(
        ahargana=ahargana_ujjain,
        chakra_cnt=chakra_cnt,
        shaka_year=shaka_year,
    )
    mandasp = manda["mandaspashta"]
    mandakarna = manda["mandakarna"]

    shighra_block = compute_shighra_block(mandaspashta=mandasp)
    sukshma = compute_sukshma_block(
        shighra_block=shighra_block,
        mandakarna_deg=mandakarna,
    )

    sp_deg = shighra_block["shighraphala_deg"]
    skantar = shighra_block["shighrakantar"]
    skendra = _extract_shighrakendra_deg(shighra_block["shighrakendra"])
    shkr_deg = sukshma["shighrakarna_deg"]
    karnanka_deg = sukshma["karnanka_deg"]
    mk_deg = sukshma["mandakarna_deg"]
    suk_deg = sukshma["sukshma_deg"]

    print("sukshma chain - kathmandu, nepal - 2025-03-30")
    print(f"ahargana_ujjain : {ahargana_ujjain:.6f}")
    print(f"chakra_cnt      : {chakra_cnt}")
    print(f"shaka_year      : {shaka_year}\n")

    header = (
        "graha      "
        "shighra_ph   "
        "shighrakantar "
        "shighrakendra "
        "karnanka    "
        "shighrakarna "
        "mandakarna "
        "sukshma"
    )
    print(header)
    print("-" * len(header))

    for g in tara_grahas:
        sp = float(sp_deg[g])
        sk = float(skantar[g])
        skd = float(skendra[g])
        kk = float(karnanka_deg.get(g, 0.0))
        shkr = float(shkr_deg.get(g, 0.0))
        mk = float(mk_deg.get(g, 0.0))
        suk = float(suk_deg[g])

        print(
            f"{g:9s}"
            f"{sp:11.6f}  "
            f"{sk:12.6f}  "
            f"{skd:12.6f}  "
            f"{kk:11.6f}  "
            f"{shkr:12.6f}  "
            f"{mk:11.6f}  "
            f"{suk:11.6f}"
        )

    print()
