# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import csv
import math
from typing import Any, Final

from bheshajpatro.utils.paths import ketaki_data_path
from bheshajpatro.core.core_functions import norm_360

__all__ = [
    "load_upakaranas",
    "ensure_loaded",
    "row_for",
    "phalanka_for",
    "calc_upakarana",
]

_upakaranas: dict[int, list[dict[str, float]]] = {}
_loaded: bool = False

cphalankas_csv_name: Final[str] = "cphalankas.csv"

_upa_coeffs: dict[int, tuple[float, float, float]] = {
    1: (0.9856100, 0.0668333333, 90.398),
    2: (12.1907490, 3.7987930000, 6.194),
    3: (11.3165062, 56.5537200000, 164.477),
    4: (13.0649920, 311.044251000, 205.562),
    5: (13.1763583, 3.9266020000, 346.269),
    6: (0.0529933, 7.7691660000, 62.375),  # negated in output
}


def _finite_float(x: Any) -> float:
    v = float(x)
    if not math.isfinite(v):
        raise TypeError(f"non-finite value {x!r}")
    return v


def load_upakaranas() -> None:
    global _upakaranas, _loaded

    csv_path = ketaki_data_path(cphalankas_csv_name)

    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        groups: dict[int, list[dict[str, float]]] = {}

        for row in reader:
            key = int(row["upakarana"])
            labdhi = int(row["labdhi"])

            entry = {
                "labdhi": labdhi,
                "phala": _finite_float(row["phala"]),
                "gamyantar": _finite_float(row["gamyantar"]),
            }
            groups.setdefault(key, []).append(entry)

    for rows in groups.values():
        rows.sort(key=lambda r: r["labdhi"])

    _upakaranas = groups
    _loaded = True


def ensure_loaded() -> None:
    global _loaded
    if not _loaded or not _upakaranas:
        load_upakaranas()


def row_for(upakarana: int, labdhi: int) -> dict[str, float]:
    rows = _upakaranas.get(upakarana)
    if rows is None:
        raise KeyError(f"unknown upakarana {upakarana}")

    for r in rows:
        if r["labdhi"] == labdhi:
            return dict(r)

    raise KeyError(f"labdhi {labdhi} missing for upakarana {upakarana}")


def phalanka_for(upakarana: int, labdhi: int) -> dict[str, float]:
    return row_for(upakarana, labdhi)


def calc_upakarana(ahargana: float, chakra_cnt: int) -> dict[int, float]:
    ah = _finite_float(ahargana)
    cc = int(chakra_cnt)

    out: dict[int, float] = {}

    for key, (gati, cycle_gati, kshepaka) in _upa_coeffs.items():
        raw = gati * ah + cycle_gati * cc + kshepaka
        if key == 6:
            raw = -raw
        out[key] = norm_360(raw)

    return out
