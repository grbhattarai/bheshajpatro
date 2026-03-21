# bheshajpatro/ketaki/grahas/shighra_chain.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bheshajpatro.engines.ketaki.core.shighrafunc.shighrakendras import (
    shighrakendra_map,
)
from bheshajpatro.engines.ketaki.core.shighrafunc.shighraphalas import (
    shighraphala_map,
)

__all__ = ["tara_grahas", "compute_shighra_block"]

tara_grahas = ("mangal", "budha", "guru", "shukra", "shani")


def compute_shighra_block(
    *,
    mandaspashta: Mapping[str, float],
) -> dict[str, Any]:
    """
    build the shighra block:

      - shighrakendra[g]["skendra"], shighrakendra[g]["sv"]
      - shighraphala_deg[g]
      - shighrakantar[g]
      - shighraphala_info[g] (full per-graha interpolation metadata)

    mandaspashta must contain 'surya' plus all tara grahas.
    """
    sk_map = shighrakendra_map(
        tara_grahas,
        graha_spashta=mandaspashta,
    )

    sv_map = {g: sk_map[g]["sv"] for g in tara_grahas}

    sp_info = shighraphala_map(
        tara_grahas,
        sv_map=sv_map,
    )

    shighraphala_deg: dict[str, float] = {
        g: sp_info[g]["value_deg"] for g in tara_grahas
    }
    shighrakantar: dict[str, float] = {
        g: sp_info[g]["gamyantar"] for g in tara_grahas
    }

    return {
        "shighrakendra": sk_map,
        "shighraphala_deg": shighraphala_deg,
        "shighrakantar": shighrakantar,
        "shighraphala_info": sp_info,
    }


if __name__ == "__main__":
    from datetime import date
    from bheshajpatro.engines.ketaki.core.anglefunc.ahargana import (
        compute_ahargana,
    )
    from bheshajpatro.engines.ketaki.grahas.manda_chain import (
        compute_manda_block,
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

    shighra_block = compute_shighra_block(mandaspashta=mandasp)

    sk_map = shighra_block["shighrakendra"]
    sp_deg = shighra_block["shighraphala_deg"]
    skantar = shighra_block["shighrakantar"]

    print("shighra chain – kathmandu, nepal – 2025-03-30")
    print(f"ahargana_ujjain : {ahargana_ujjain:.6f}")
    print(f"chakra_cnt      : {chakra_cnt}")
    print(f"shaka_year      : {shaka_year}\n")

    header = (
        "graha      "
        "manda_spa      "
        "skendra     "
        "sv         "
        "shighra_ph   "
        "shighrakantar "
    )
    print(header)
    print("-" * len(header))

    for g in tara_grahas:
        ms = float(mandasp[g])
        sk = float(sk_map[g]["skendra"])
        sv = float(sk_map[g]["sv"])
        sp = float(sp_deg[g])
        sknt = float(skantar[g])

        print(
            f"{g:9s}"
            f"{ms:12.6f}  "
            f"{sk:10.6f}  "
            f"{sv:10.6f}  "
            f"{sp:11.6f}  "
            f"{sknt:13.6f}"
        )

    print()
