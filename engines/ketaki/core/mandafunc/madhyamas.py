# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable, Mapping

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.ketaki.core.constants import (
    madhyama_dhruba,
    madhyama_gati,
    madhyama_kshepaka,
)

__all__ = ["madhyama_one", "calc_madhyama"]


def _get(map_: Mapping[str, float], graha: str) -> float:
    key = graha.strip().lower()
    if key not in map_:
        raise KeyError(f"{key!r} not found in constant map")
    return float(map_[key])


def madhyama_one(
    graha: str,
    *,
    ahargana: float,
    chakra_count: int,
    beeja_map: Mapping[str, float],
    gati_map: Mapping[str, float] = madhyama_gati,
    dhruba_map: Mapping[str, float] = madhyama_dhruba,
    kshepaka_map: Mapping[str, float] = madhyama_kshepaka,
) -> float:
    g = graha.strip().lower()
    const_key = "rahu" if g == "ketu" else g

    daily = float(ahargana) * _get(gati_map, const_key)
    cycle = int(chakra_count) * _get(dhruba_map, const_key)
    base = _get(kshepaka_map, const_key)
    beeja = float(beeja_map.get(const_key, 0.0))

    if const_key == "rahu":
        daily = -daily

    lon = norm_360(daily + cycle + base + beeja)

    if g == "ketu":
        lon = norm_360(lon + 180.0)

    return lon


def calc_madhyama(
    grahas: Iterable[str],
    *,
    ahargana: float,
    chakra_count: int,
    beeja_map: Mapping[str, float],
    gati_map: Mapping[str, float] = madhyama_gati,
    dhruba_map: Mapping[str, float] = madhyama_dhruba,
    kshepaka_map: Mapping[str, float] = madhyama_kshepaka,
) -> dict[str, float]:
    return {
        g: madhyama_one(
            g,
            ahargana=ahargana,
            chakra_count=chakra_count,
            beeja_map=beeja_map,
            gati_map=gati_map,
            dhruba_map=dhruba_map,
            kshepaka_map=kshepaka_map,
        )
        for g in grahas
    }