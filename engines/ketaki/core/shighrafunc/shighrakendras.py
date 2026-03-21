# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from bheshajpatro.core.core_functions import norm_360, calc_shadvalpa

__all__ = [
    "ShighrakendraResult",
    "shighrakendra_one",
    "shighrakendra_map",
]


class ShighrakendraResult(TypedDict):
    graha: str
    skendra: float
    sv: float


def shighrakendra_one(
    graha: str,
    *,
    graha_spashta: Mapping[str, float],
) -> ShighrakendraResult:
    g = graha.strip().lower()

    gval = graha_spashta[g]
    sval = graha_spashta["surya"]

    sk = norm_360(gval - sval)
    sv = calc_shadvalpa(sk)

    return {
        "graha": g,
        "skendra": float(sk),
        "sv": float(sv),
    }


def shighrakendra_map(
    grahas: tuple[str, ...] | list[str],
    *,
    graha_spashta: Mapping[str, float],
) -> dict[str, ShighrakendraResult]:
    return {
        g: shighrakendra_one(g, graha_spashta=graha_spashta)
        for g in grahas
    }
