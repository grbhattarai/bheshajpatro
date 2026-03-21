# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

__all__ = [
    "madhyama_kshepaka",
    "mandocha_kshepaka",
    "madhyama_dhruba",
    "mandocha_dhruba",
    "madhyama_gati",
    "madhyama_karna",
    "const",
    "categories",
    "grahas",
    "get_const",
]

# ----------------------------------------------------------------------
# Core constant maps (all keyed by canonical graha names):
#   "surya", "chandra", "mangal", "budha",
#   "guru", "shukra", "shani", "rahu"
# Ketu is always handled as anti-Rahu at the algorithm level.
# ----------------------------------------------------------------------

madhyama_kshepaka: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 349.083333333,
        "chandra": 355.283333333,
        "uchandra": 327.366666667,
        "rahu": 297.616666667,
        "mangal": 69.200000000,
        "budha": 52.500000000,
        "guru": 275.666666667,
        "shukra": 195.466666667,
        "shani": 338.350000000,
    }
)

mandocha_kshepaka: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 78.683333333,
        "mangal": 131.683333333,
        "budha": 233.433333333,
        "guru": 170.216666667,
        "shukra": 287.666666667,
        "shani": 248.450000000,
    }
)

madhyama_dhruba: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 0.1272222222,
        "chandra": 3.9266666667,
        "uchandra": 52.8822222222,
        "rahu": 352.2327777778,
        "mangal": 36.7888888889,
        "budha": 320.8305555556,
        "guru": 216.6533333333,
        "shukra": 318.7861111111,
        "shani": 232.2102777778,
    }
)

mandocha_dhruba: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 0.06250000,
        "mangal": 0.08916667,
        "budha": 0.03250000,
        "guru": 0.03500000,
        "shukra": 0.00791667,
        "shani": 0.08416667,
    }
)

madhyama_gati: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 0.98560910,
        "chandra": 13.17635830,
        "uchandra": 0.11136630,
        "rahu": 0.05299240,
        "mangal": 0.52403299,
        "budha": 4.09233871,
        "guru": 0.08309127,
        "shukra": 1.60213057,
        "shani": 0.03345967,
    }
)

madhyama_karna: Final[Mapping[str, float]] = MappingProxyType(
    {
        "surya": 100.0,
        "mangal": 152.0,
        "budha": 39.0,
        "guru": 520.0,
        "shukra": 72.0,
        "shani": 954.0,
    }
)

# ----------------------------------------------------------------------
# Aggregate view + helpers
# ----------------------------------------------------------------------

const: Final[Mapping[str, Mapping[str, float]]] = MappingProxyType(
    {
        "madhyama_kshepaka": madhyama_kshepaka,
        "mandocha_kshepaka": mandocha_kshepaka,
        "madhyama_dhruba": madhyama_dhruba,
        "mandocha_dhruba": mandocha_dhruba,
        "madhyama_gati": madhyama_gati,
        "madhyama_karna": madhyama_karna,
    }
)

categories: Final[tuple[str, ...]] = tuple(const.keys())

# Base grahas from constant tables; explicitly add "ketu" to canonical list.
_base_grahas = {g for group in const.values() for g in group}
_base_grahas.add("ketu")

grahas: Final[tuple[str, ...]] = tuple(sorted(_base_grahas))


def get_const(category: str, graha: str) -> float:
    """
    Look up a constant value for a given category and graha.

    Parameters
    ----------
    category:
        One of the keys in `const`, e.g. "madhyama_kshepaka".
    graha:
        Canonical graha name (case-insensitive).

    Returns
    -------
    float
        The constant value.
    """
    return float(const[category][graha.lower()])
