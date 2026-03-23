# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable, Mapping

from bheshajpatro.core.core_functions import calc_shadvalpa, norm_360

__all__ = [
    "calc_mandakendra",
    "calc_mkshadvalpa",
]


def calc_mandakendra(
    *,
    madhyama: Mapping[str, float],
    mandocha: Mapping[str, float],
    grahas: Iterable[str] | None = None,
) -> dict[str, float]:
    if grahas is None:
        grahas = sorted(set(madhyama.keys()) & set(mandocha.keys()))

    return {g: norm_360(madhyama[g] - mandocha[g]) for g in grahas}


def calc_mkshadvalpa(
    *,
    madhyama: Mapping[str, float],
    mandocha: Mapping[str, float],
    grahas: Iterable[str] | None = None,
) -> dict[str, float]:
    mk = calc_mandakendra(
        madhyama=madhyama,
        mandocha=mandocha,
        grahas=grahas,
    )
    return {g: calc_shadvalpa(v) for g, v in mk.items()}