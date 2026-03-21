# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
# pure ascii-only, strict lowercase

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TypedDict

from bheshajpatro.engines.ketaki.core.anglefunc.labdhis import (
    calc_phalanka,
    phalanka_info,
)

__all__ = [
    "mandaphala_one",
    "mandaphala_map",
]


class MandaphalaResult(TypedDict):
    graha: str
    value_deg: float
    labdhi: float
    shesha: float
    gamyantar: float


def mandaphala_one(
    graha: str,
    *,
    sv: float,
) -> MandaphalaResult:
    info = phalanka_info("mandaphala", graha, sv)
    base = calc_phalanka("mandaphala", graha, sv)

    g = graha.strip().lower()
    if g == "surya":
        # surya mandaphala table is in minutes
        val_deg = float(base) / 60.0
    else:
        # other grahas: table value × 0.1 → degrees
        val_deg = float(base) * 0.1

    return {
        "graha": g,
        "value_deg": float(val_deg),
        "labdhi": float(info["labdhi_index"]),
        "shesha": float(info["shesha"]),
        "gamyantar": float(info["diff"]),
    }


def mandaphala_map(
    grahas: Iterable[str],
    *,
    sv_map: Mapping[str, float],
) -> dict[str, MandaphalaResult]:
    return {g: mandaphala_one(g, sv=sv_map[g]) for g in grahas}
