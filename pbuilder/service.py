# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Literal

from bheshajpatro.core.models import PanchangaResponse, PanchangaResult
from bheshajpatro.engines.session_orchestrator import build_engine_sessions_for_date

EngineName = Literal["drik", "ketaki"]


def _normalize_engine(engine: str | EngineName) -> EngineName:
    e = str(engine).lower().strip()
    if e not in {"drik", "ketaki"}:
        raise ValueError(f"unknown engine '{engine}', expected 'drik' or 'ketaki'.")
    return e  # type: ignore[return-value]


def get_panchanga_session(
    date_ce: date,
    place: Dict[str, Any],
    engine: str | EngineName = "drik",
    include_monthly: bool = False,
) -> Dict[str, Any]:
    """
    Build a panchanga session for the given engine.

    Expected place keys:
      - latitude
      - longitude
      - standard
      - tz
      - elevation (optional)
    """
    eng = _normalize_engine(engine)

    lat = float(place["latitude"])
    lon = float(place["longitude"])
    std = float(place["standard"])
    tz = place.get("tz") or None
    elevation = float(place.get("elevation", 0.0))

    engine_sessions = build_engine_sessions_for_date(
        engine=eng,
        d=date_ce,
        latitude_deg=lat,
        longitude_deg=lon,
        standard_meridian_deg=std,
        tz_name=tz,
        elevation_m=elevation,
        include_monthly=include_monthly,
    )

    daily = engine_sessions["daily"]
    context: Dict[str, Any] = daily.get("context", {})
    astro: Dict[str, Any] = daily.get("astro", {})
    panchanga_result: Dict[str, Any] = astro.get("panchanga_result", {})

    return {
        "context": context,
        "products": {
            "main": {
                "panchanga_result": panchanga_result,
                "astro": astro,
            },
            "monthly": engine_sessions.get("monthly", {}),
        },
    }


def get_panchanga_result(
    date_ce: date,
    place: Dict[str, Any],
    engine: str | EngineName = "drik",
) -> PanchangaResponse:
    session = get_panchanga_session(date_ce, place, engine=engine)
    context: Dict[str, Any] = session["context"]
    astro_main: Dict[str, Any] = session["products"]["main"]
    result_raw: Dict[str, Any] = astro_main["panchanga_result"]

    result = PanchangaResult(**result_raw)
    return PanchangaResponse(context=context, result=result)