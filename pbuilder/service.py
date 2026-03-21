# bheshajpatro/pbuilder/service.py

from __future__ import annotations

from datetime import date
from typing import Dict, Any, Literal

from bheshajpatro.core.models import PanchangaResponse, PanchangaResult
from zz_legacy.app.session_orchestrator import build_engine_sessions_for_date


EngineName = Literal["drik", "ketaki"]


def _normalize_engine(engine: str | EngineName) -> EngineName:
    e = str(engine).lower()
    if e not in {"drik", "ketaki"}:
        raise ValueError(f"unknown engine '{engine}', expected 'drik' or 'ketaki'.")
    return e  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# shared session / daily bheshajpatro helpers
# ---------------------------------------------------------------------------

def get_panchanga_session(
    date_ce: date,
    place: Dict[str, Any],
    engine: str | EngineName = "ketaki",
) -> Dict[str, Any]:
    """
    build a bheshajpatro computation session for the given engine.

    this now uses the unified drik/ketaki engine pipeline via
    app.session_orchestrator.build_engine_sessions_for_date.

    expected input `place` keys:
      - latitude
      - longitude
      - standard  (standard meridian, degrees)
      - tz        (iana tz name, lowercased)
    """

    eng = _normalize_engine(engine)

    lat = float(place["latitude"])
    lon = float(place["longitude"])
    std = float(place["standard"])
    tz = (place.get("tz") or None)  # keep None if empty

    engine_sessions = build_engine_sessions_for_date(
        engine=eng,
        d=date_ce,
        latitude_deg=lat,
        longitude_deg=lon,
        standard_meridian_deg=std,
        tz_name=tz,
        elevation_m=0.0,
        ephe_dir=None,
    )

    daily = engine_sessions["daily"]
    context: Dict[str, Any] = daily.get("context", {})
    astro: Dict[str, Any] = daily.get("astro", {})

    panchanga_result: Dict[str, Any] = astro.get("panchanga_result", {})

    session: Dict[str, Any] = {
        "context": context,
        "products": {
            "main": {
                "panchanga_result": panchanga_result,
                "astro": astro,
            },
            "monthly": engine_sessions.get("monthly", {}),
        },
    }

    return session


def get_panchanga_result(
    date_ce: date,
    place: Dict[str, Any],
    engine: str | EngineName = "ketaki",
) -> PanchangaResponse:
    """
    high-level helper that runs the selected engine and returns
    a structured PanchangaResponse suitable for the web api.

    expects get_panchanga_session() to return a session dict with:

        session["context"]                -> context dict
        session["products"]["main"]
               ["panchanga_result"]       -> daily bheshajpatro dict

    which matches PanchangaResult fields.
    """

    session = get_panchanga_session(date_ce, place, engine=engine)
    context: Dict[str, Any] = session["context"]
    astro_main: Dict[str, Any] = session["products"]["main"]
    result_raw: Dict[str, Any] = astro_main["panchanga_result"]

    result = PanchangaResult(**result_raw)
    return PanchangaResponse(context=context, result=result)


# ---------------------------------------------------------------------------
# optional: drik ephemeris helper (not wired yet)
# ---------------------------------------------------------------------------

def get_drik_ephemeris(
    date_ce: date,
    place: Dict[str, Any],
) -> Dict[str, Any]:
    """
    placeholder for a future drik/swiss ephemeris endpoint.

    you can implement this later using your actual drik engine
    (e.g. core + grahas), but for now it's a stub so imports succeed.
    """
    raise NotImplementedError("get_drik_ephemeris is not implemented yet.")
