# bheshajpatro/ketaki/grahas/taragati_chain.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping

from bheshajpatro.engines.ketaki.core.constants import madhyama_gati

__all__ = ["compute_panchatara_gati"]

tara_grahas = ("mangal", "budha", "guru", "shukra", "shani")


def _manda_component(mandakantar: Mapping[str, float]) -> dict[str, float]:
    """
    manda-phala contribution to gati, in degrees per day.
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
    for g in tara_grahas:
        mk = mandakantar.get(g)
        if mk is None:
            continue
        mins = (mk / div[g]) * budha_mul if g == "budha" else (mk / div[g])
        out[g] = mins / 60.0
    return out


def _shighra_component(shighrakantar: Mapping[str, float]) -> dict[str, float]:
    """
    shighra-phala contribution to gati, in degrees per day.

    sign: gatishighraphala follows sign of sk automatically.
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
    for g in tara_grahas:
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
    combine manda-phala and shighra-phala corrections into final tara gati.
    """
    base = {g: float(madhyama_gati[g]) for g in tara_grahas}

    gm = _manda_component(mandakantar)
    mandagati = {g: base[g] - gm.get(g, 0.0) for g in tara_grahas}

    gs = _shighra_component(shighrakantar)

    shigr: dict[str, float] = {}
    for g in tara_grahas:
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
    mandakantar = manda["mandakantar"]

    shighra_block = compute_shighra_block(mandaspashta=manda["mandaspashta"])
    shighrakantar = shighra_block["shighrakantar"]

    surya_gati = float(madhyama_gati["surya"])

    tara = compute_panchatara_gati(
        mandakantar=mandakantar,
        shighrakantar=shighrakantar,
        surya_gati=surya_gati,
    )

    gm = tara["gatimandaphala"]
    mandagati = tara["mandagati"]
    gs = tara["gatishighraphala"]
    shigr = tara["shighragati"]

    print("tara gati chain - kathmandu, nepal - 2025-03-30")
    print(f"ahargana_ujjain : {ahargana_ujjain:.6f}")
    print(f"chakra_cnt      : {chakra_cnt}")
    print(f"shaka_year      : {shaka_year}")
    print(f"surya_gati      : {surya_gati:.6f}\n")

    header = (
        "graha      "
        "mandakantar "
        "gatimanda_ph "
        "mandagati   "
        "shighrakantar "
        "gatishighra_ph "
        "shighragati"
    )
    print(header)
    print("-" * len(header))

    for g in tara_grahas:
        mk = float(mandakantar.get(g, 0.0))
        gmp = float(gm.get(g, 0.0))
        mdg = float(mandagati.get(g, 0.0))
        sk = float(shighrakantar.get(g, 0.0))
        gsp = float(gs.get(g, 0.0))
        sgr = float(shigr.get(g, 0.0))

        print(
            f"{g:9s}"
            f"{mk:11.6f}  "
            f"{gmp:12.6f}  "
            f"{mdg:11.6f}  "
            f"{sk:14.6f}  "
            f"{gsp:14.6f}  "
            f"{sgr:11.6f}"
        )

    print()
