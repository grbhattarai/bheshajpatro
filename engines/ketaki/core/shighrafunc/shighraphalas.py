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
    "ShighraphalaResult",
    "shighraphala_one",
    "shighraphala_map",
]


class ShighraphalaResult(TypedDict):
    graha: str
    value_deg: float
    labdhi: float
    shesha: float
    gamyantar: float


def shighraphala_one(
    graha: str,
    *,
    sv: float,
) -> ShighraphalaResult:
    g = graha.strip().lower()

    info = phalanka_info("shighraphala", g, sv)
    base = calc_phalanka("shighraphala", g, sv)
    val_deg = float(base) * 0.1

    return {
        "graha": g,
        "value_deg": val_deg,
        "labdhi": float(info["labdhi_index"]),
        "shesha": float(info["shesha"]),
        "gamyantar": float(info["diff"]),
    }


def shighraphala_map(
    grahas: tuple[str, ...] | list[str],
    *,
    sv_map: Mapping[str, float],
) -> dict[str, ShighraphalaResult]:
    return {
        g: shighraphala_one(g, sv=sv_map[g])
        for g in grahas
    }
