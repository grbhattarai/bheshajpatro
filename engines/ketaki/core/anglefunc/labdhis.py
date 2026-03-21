# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite

from bheshajpatro.engines.ketaki.core.constants import jyotish_lookup

__all__ = [
    "sv_to_labdhi",
    "calc_phalanka",
    "phalanka_info",
    "rows",
    "columns",
    "clamp_labdhi",
]

# linear interpolation step is always 10° of shadvalpa
_INTERP_DENOM = 10.0


def _to_float_finite(value: object, name: str = "value") -> float:
    """Convert to float and ensure the value is finite."""
    v = float(value)
    if not isfinite(v):
        raise TypeError(f"{name} must be finite, got {value!r}")
    return v


def rows(table_name: str) -> Mapping[int, Mapping[str, float]]:
    """Return the full labdhi table for a given name."""
    # Let KeyError propagate if table_name is invalid
    return jyotish_lookup[table_name]


def columns(table_name: str) -> list[str]:
    """Return column names for a given table."""
    tbl = rows(table_name)
    first_row = next(iter(tbl.values()))
    return list(first_row.keys())


def clamp_labdhi(table_name: str, labdhi_index: int) -> int:
    """Clamp labdhi index into the valid [min, max] range for the table."""
    tbl = rows(table_name)
    kmin = min(tbl.keys())
    kmax = max(tbl.keys())
    return max(min(int(labdhi_index), kmax), kmin)


def sv_to_labdhi(shadvalpa: float) -> tuple[int, float]:
    """
    Convert shadvalpa (0..180) to (labdhi_index, shesha_deg).

    Step size is 10°; shesha is the remainder within that interval.
    """
    sv = max(0.0, min(_to_float_finite(shadvalpa, "shadvalpa"), 180.0))
    idx = int(sv // _INTERP_DENOM)
    shesha = sv - _INTERP_DENOM * idx
    if abs(shesha) < 1e-12:
        shesha = 0.0
    return idx, shesha


def _get(row: Mapping[str, float], col: str) -> float:
    key = col.strip().lower()
    if key not in row:
        raise KeyError(f"column {key!r} not in {list(row.keys())}")
    return _to_float_finite(row[key], f"row[{key}]")


def phalanka_info(
    table_name: str,
    column_name: str,
    shadvalpa: float,
    next_column_name: str | None = None,
) -> dict[str, float | str]:
    """
    Interpolate phalanka value and return detailed info for debugging/inspection.
    """
    tbl = rows(table_name)
    idx, shesha = sv_to_labdhi(shadvalpa)

    row0 = tbl.get(idx)
    row1 = tbl.get(idx + 1, row0)

    if row0 is None:
        raise KeyError(f"missing labdhi row {idx} for table {table_name!r}")

    col0 = column_name
    col1 = next_column_name or col0

    v0 = _get(row0, col0)
    v1 = _get(row1, col1)
    diff = v1 - v0

    phalanka = v0 + (shesha / _INTERP_DENOM) * diff

    norm_col0 = col0.strip().lower()
    norm_col1 = col1.strip().lower()

    return {
        "table": table_name,
        "column": f"{norm_col0}->{norm_col1}" if norm_col0 != norm_col1 else norm_col0,
        "labdhi_index": float(idx),
        "shesha": float(shesha),
        "start": float(v0),
        "end": float(v1),
        "diff": float(diff),
        "denom": float(_INTERP_DENOM),
        "phalanka": float(phalanka),
    }


def calc_phalanka(
    table_name: str,
    column_name: str,
    shadvalpa: float,
    next_column_name: str | None = None,
) -> float:
    """Simple wrapper: return just the interpolated phalanka value."""
    info = phalanka_info(
        table_name=table_name,
        column_name=column_name,
        shadvalpa=shadvalpa,
        next_column_name=next_column_name,
    )
    return float(info["phalanka"])
