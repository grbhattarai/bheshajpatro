# bheshajpatro/engines/ketaki/core/mandafunc/mandakarnas.py
# pure ascii-only, strict lowercase
# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import (
    calc_phalanka,
    phalanka_info,
)

__all__ = [
    "mandakarna_grahas",
    "mandakarna_one",
    "mandakarna_map",
]


class MandakarnaResult(TypedDict):
    graha: str
    value_deg: float
    labdhi: float
    shesha: float
    gamyantar: float


# Only these grahas use mandakarna tables
mandakarna_grahas: tuple[str, ...] = ("mangal", "budha")


def mandakarna_one(
    graha: str,
    *,
    sv: float,
) -> MandakarnaResult:
    """Compute mandakarna for a single graha."""
    g = graha.strip().lower()

    info = phalanka_info("mandakarna", g, sv)
    base = calc_phalanka("mandakarna", g, sv)

    return {
        "graha": g,
        "value_deg": float(base),   # mandakarna has no scaling
        "labdhi": float(info["labdhi_index"]),
        "shesha": float(info["shesha"]),
        "gamyantar": float(info["diff"]),
    }


def mandakarna_map(
    *,
    sv_map: Mapping[str, float],
    grahas: tuple[str, ...] | None = None,
) -> dict[str, MandakarnaResult]:
    """
    Compute mandakarna for all grahas in list, default = mandakarna_grahas.
    Only grahas present in both `sv_map` and mandakarna_grahas are processed.
    """
    use_grahas = grahas or mandakarna_grahas

    return {
        g: mandakarna_one(g, sv=sv_map[g])
        for g in use_grahas
        if g in sv_map and g in mandakarna_grahas
    }
