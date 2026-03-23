# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from bheshajpatro.core.core_functions import calc_shadvalpa, norm_360

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

    if g not in graha_spashta:
        raise KeyError(f"{g!r} not found in graha_spashta")
    if "surya" not in graha_spashta:
        raise KeyError("'surya' not found in graha_spashta")

    gval = float(graha_spashta[g])
    sval = float(graha_spashta["surya"])

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