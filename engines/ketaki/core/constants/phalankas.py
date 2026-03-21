# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable, Mapping
from math import isfinite
from types import MappingProxyType

__all__ = [
    "jyotish_lookup",
    "get_headers",
    "get_row",
    "get_phalanka",
]


def _float(x: object) -> float:
    v = float(x)
    if not isfinite(v):
        raise TypeError(f"value {x!r} must be finite")
    return v


def _build_table(
    headers: Iterable[str],
    rows: Iterable[Iterable[object]],
) -> Mapping[int, Mapping[str, float]]:
    cols = tuple(h.strip().lower() for h in headers)
    out: dict[int, dict[str, float]] = {}

    for row in rows:
        items = tuple(row)
        if len(items) != len(cols) + 1:
            raise ValueError(f"row length mismatch: {items}")

        labdhi = int(items[0])
        if labdhi in out:
            raise ValueError(f"duplicate labdhi row: {labdhi}")

        out[labdhi] = {
            cols[i]: _float(items[i + 1])
            for i in range(len(cols))
        }

    if set(out.keys()) != set(range(19)):
        raise ValueError(f"labdhi rows must be 0..18, got {sorted(out.keys())}")

    return MappingProxyType(
        {k: MappingProxyType(v) for k, v in sorted(out.items())}
    )


_tables: dict[str, Mapping[int, Mapping[str, float]]] = {}


def _add(
    name: str,
    headers: Iterable[str],
    rows: Iterable[Iterable[object]],
) -> None:
    _tables[name] = _build_table(headers, rows)

# --------------------------------------------------------------------------
# TABLE DEFINITIONS (unchanged)
# --------------------------------------------------------------------------

_add(
    "mandaphala",
    ("surya", "mangal", "budha", "guru", "shukra", "shani"),
    [
        [0, 0, 0, 0, 0, 0, 0],
        [1, 20, 17, 32, 9, 1, 10],
        [2, 39, 33, 65, 18, 3, 21],
        [3, 57, 48, 96, 26, 4, 30],
        [4, 73, 63, 125, 34, 5, 39],
        [5, 87, 76, 153, 41, 6, 47],
        [6, 99, 87, 178, 46, 7, 54],
        [7, 108, 96, 199, 51, 7, 59],
        [8, 113, 103, 217, 54, 8, 63],
        [9, 115, 106, 229, 55, 8, 64],
        [10, 114, 107, 236, 55, 8, 64],
        [11, 109, 104, 236, 53, 7, 62],
        [12, 101, 98, 228, 49, 7, 58],
        [13, 89, 88, 211, 44, 6, 52],
        [14, 75, 75, 185, 37, 6, 45],
        [15, 59, 59, 149, 29, 5, 34],
        [16, 40, 41, 105, 20, 3, 24],
        [17, 20, 21, 54, 10, 1, 12],
        [18, 0, 0, 0, 0, 0, 0],
    ],
)

_add(
    "shighraphala",
    ("mangal", "budha", "guru", "shukra", "shani"),
    [
        [0, 0, 0, 0, 0, 0],
        [1, 40, 28, 16, 42, 9],
        [2, 79, 55, 32, 84, 19],
        [3, 118, 82, 47, 125, 28],
        [4, 157, 109, 62, 167, 36],
        [5, 195, 134, 75, 206, 43],
        [6, 232, 157, 86, 247, 49],
        [7, 267, 178, 96, 286, 54],
        [8, 301, 197, 104, 323, 58],
        [9, 333, 212, 109, 359, 60],
        [10, 361, 222, 111, 392, 60],
        [11, 385, 227, 109, 421, 58],
        [12, 402, 226, 104, 445, 55],
        [13, 410, 215, 95, 460, 49],
        [14, 403, 195, 82, 462, 42],
        [15, 372, 162, 66, 441, 33],
        [16, 304, 118, 46, 377, 23],
        [17, 179, 62, 24, 236, 12],
        [18, 0, 0, 0, 0, 0],
    ],
)

_add(
    "mandakarna",
    ("mangal", "budha"),
    [
        [0, 166, 47],
        [1, 166, 47],
        [2, 166, 46],
        [3, 165, 46],
        [4, 164, 45],
        [5, 162, 45],
        [6, 160, 44],
        [7, 158, 43],
        [8, 156, 42],
        [9, 154, 40],
        [10, 151, 39],
        [11, 149, 38],
        [12, 146, 37],
        [13, 144, 35],
        [14, 142, 33],
        [15, 140, 32],
        [16, 139, 32],
        [17, 138, 31],
        [18, 138, 31],
    ],
)

_add(
    "karnanka",
    ("mangal", "budha", "guru", "shukra", "shani"),
    [
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1],
        [2, 3, 2, 5, 2, 6],
        [3, 8, 4, 11, 5, 12],
        [4, 16, 7, 20, 10, 21],
        [5, 22, 11, 30, 15, 33],
        [6, 32, 15, 43, 22, 46],
        [7, 43, 20, 58, 30, 61],
        [8, 56, 26, 73, 39, 78],
        [9, 70, 32, 90, 49, 95],
        [10, 85, 38, 108, 59, 112],
        [11, 101, 45, 125, 71, 130],
        [12, 118, 52, 142, 83, 146],
        [13, 135, 58, 158, 95, 161],
        [14, 153, 64, 172, 108, 174],
        [15, 169, 70, 183, 120, 185],
        [16, 184, 74, 192, 132, 193],
        [17, 195, 77, 198, 141, 198],
        [18, 200, 78, 200, 144, 200],
    ],
)

_add(
    "suryagati",
    ("surya",),
    [
        [0, 57.1],
        [1, 57.2],
        [2, 57.3],
        [3, 57.4],
        [4, 57.6],
        [5, 57.8],
        [6, 58.1],
        [7, 58.4],
        [8, 58.7],
        [9, 59.1],
        [10, 59.4],
        [11, 59.7],
        [12, 60.1],
        [13, 60.4],
        [14, 60.7],
        [15, 60.9],
        [16, 61.0],
        [17, 61.1],
        [18, 61.1],
    ],
)

_add(
    "suryakranti",
    ("surya",),
    [
        [0, 0],
        [1, 238],
        [2, 469],
        [3, 689],
        [4, 889],
        [5, 1065],
        [6, 1210],
        [7, 1315],
        [8, 1385],
        [9, 1407],
        [10, 1385],
        [11, 1315],
        [12, 1210],
        [13, 1065],
        [14, 889],
        [15, 689],
        [16, 469],
        [17, 238],
        [18, 0],
    ],
)

jyotish_lookup: Mapping[str, Mapping[int, Mapping[str, float]]] = MappingProxyType(
    dict(_tables)
)

# --------------------------------------------------------------------------
# Simple Accessors
# --------------------------------------------------------------------------

def get_headers(name: str) -> list[str]:
    table = jyotish_lookup[name]
    return list(next(iter(table.values())).keys())


def get_row(name: str, labdhi: int) -> Mapping[str, float]:
    return jyotish_lookup[name][int(labdhi)]


def get_phalanka(name: str, labdhi: int, graha: str) -> float:
    return jyotish_lookup[name][int(labdhi)][graha.strip().lower()]
