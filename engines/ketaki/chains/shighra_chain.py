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

__all__ = ["TARA_GRAHAS", "compute_shighra_block"]

TARA_GRAHAS = ("mangal", "budha", "guru", "shukra", "shani")


def compute_shighra_block(
    *,
    mandaspashta: Mapping[str, float],
) -> dict[str, Any]:
    """
    Build the shighra block.

    Returns:
      - shighrakendra[g]["skendra"], shighrakendra[g]["sv"]
      - shighraphala_deg[g]
      - shighrakantar[g]
      - shighraphala_info[g] (full per-graha interpolation metadata)

    `mandaspashta` must contain 'surya' plus all tara grahas.
    """
    sk_map = shighrakendra_map(
        TARA_GRAHAS,
        graha_spashta=mandaspashta,
    )

    sv_map = {g: sk_map[g]["sv"] for g in TARA_GRAHAS}

    sp_info = shighraphala_map(
        TARA_GRAHAS,
        sv_map=sv_map,
    )

    shighraphala_deg: dict[str, float] = {
        g: sp_info[g]["value_deg"] for g in TARA_GRAHAS
    }
    shighrakantar: dict[str, float] = {
        g: sp_info[g]["gamyantar"] for g in TARA_GRAHAS
    }

    return {
        "shighrakendra": sk_map,
        "shighraphala_deg": shighraphala_deg,
        "shighrakantar": shighrakantar,
        "shighraphala_info": sp_info,
    }