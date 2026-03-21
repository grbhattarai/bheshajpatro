# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable, Mapping

from bheshajpatro.core.core_functions import norm_360
from bheshajpatro.engines.ketaki.core.constants import (
    mandocha_dhruba,
    mandocha_kshepaka,
)

__all__ = ["mandocha_one", "calc_mandocha"]

DEFAULT_SCALE = 6940.0


def _get(map_: Mapping[str, float], graha: str) -> float:
    return float(map_[graha.strip().lower()])


def mandocha_one(
    graha: str,
    *,
    ahargana: float,
    chakra_count: int,
    dhruba_map: Mapping[str, float] = mandocha_dhruba,
    kshepaka_map: Mapping[str, float] = mandocha_kshepaka,
    ahargana_scale: float = DEFAULT_SCALE,
) -> float:
    u_d = _get(dhruba_map, graha)
    u_k = _get(kshepaka_map, graha)
    pos = u_k + chakra_count * u_d + (ahargana * u_d / ahargana_scale)
    return norm_360(pos)


def calc_mandocha(
    grahas: Iterable[str],
    *,
    ahargana: float,
    chakra_count: int,
    dhruba_map: Mapping[str, float] = mandocha_dhruba,
    kshepaka_map: Mapping[str, float] = mandocha_kshepaka,
    ahargana_scale: float = DEFAULT_SCALE,
) -> dict[str, float]:
    return {
        g: mandocha_one(
            g,
            ahargana=ahargana,
            chakra_count=chakra_count,
            dhruba_map=dhruba_map,
            kshepaka_map=kshepaka_map,
            ahargana_scale=ahargana_scale,
        )
        for g in grahas
    }
