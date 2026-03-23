# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date
from typing import Any, Dict

from bheshajpatro.engines.registry import ENGINE_RUNNERS
from bheshajpatro.pbuilder.daypanchanga import run as build_day_panchanga
from bheshajpatro.pbuilder.monthpanchanga import build_month_panchanga_from_daily


def build_engine_sessions_for_date(
    engine: str,
    d: date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float = 0.0,
    include_monthly: bool = False,
) -> Dict[str, Any]:
    engine_key = str(engine).lower().strip()

    try:
        daily_engine_run = ENGINE_RUNNERS[engine_key]
    except KeyError as exc:
        raise ValueError(f"Unknown engine '{engine}'.") from exc

    # 1) Engine-specific raw daily session
    raw_daily = daily_engine_run(
        d,
        latitude_deg,
        longitude_deg,
        standard_meridian_deg,
        tz_name,
        elevation_m,
    )

    # 2) Engine-agnostic panchanga builder
    daily = build_day_panchanga(raw_daily)

    # 3) Monthly bundle — only when explicitly requested
    monthly_rows = []
    if include_monthly:
        monthly_rows = build_month_panchanga_from_daily(
            d=d,
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            standard_meridian_deg=standard_meridian_deg,
            tz_name=tz_name,
            elevation_m=elevation_m,
            daily_engine_run=daily_engine_run,
        )

    return {
        "daily": daily,
        "monthly": {
            "rows": monthly_rows,
        },
    }