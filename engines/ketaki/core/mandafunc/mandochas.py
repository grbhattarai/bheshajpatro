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

# Traditional scaling factor used in mandocha progression
DEFAULT_SCALE = 6940.0


def _get(map_: Mapping[str, float], graha: str) -> float:
    key = graha.strip().lower()
    if key not in map_:
        raise KeyError(f"{key!r} not found in constant map")
    return float(map_[key])


def mandocha_one(
    graha: str,
    *,
    ahargana: float,
    chakra_count: int,
    dhruba_map: Mapping[str, float] = mandocha_dhruba,
    kshepaka_map: Mapping[str, float] = mandocha_kshepaka,
    ahargana_scale: float = DEFAULT_SCALE,
) -> float:
    g = graha.strip().lower()

    u_d = _get(dhruba_map, g)
    u_k = _get(kshepaka_map, g)

    ah = float(ahargana)
    cc = int(chakra_count)

    pos = u_k + cc * u_d + (ah * u_d / float(ahargana_scale))

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