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
    ephe_dir: str | None = None,
) -> Dict[str, Any]:
    engine_key = str(engine).lower().strip()

    if engine_key not in ENGINE_RUNNERS:
        raise ValueError(f"Unknown engine '{engine}'.")

    daily_engine_run = ENGINE_RUNNERS[engine_key]

    # 1) engine raw daily session
    daily = daily_engine_run(
        d,
        latitude_deg,
        longitude_deg,
        standard_meridian_deg,
        tz_name,
        elevation_m,
    )

    # 2) engine-agnostic panchanga builder
    daily = build_day_panchanga(daily)

    # 3) optional monthly bundle
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