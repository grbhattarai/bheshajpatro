# bheshajpatro/utils/runtime.py
"""
Minimal runtime helpers for the new Panchanga engine structure.

The old architecture had:
- monthly caching
- validate_place / validate_date
- ketaki_daily / ketaki_monthly
- drik_daily / drik_monthly
- sessions written to JSON
- complex engine dispatch

All of that is removed.

We only expose simple helpers used by get_panchanga_session().
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict


def build_session_drik(date_ce: date, place: Dict[str, Any], write_csv: bool = False) -> Dict[str, Any]:
    """
    Wrapper used by pbuilder.service.get_panchanga_session().
    Creates a minimal session dict containing the inputs and
    whatever the Drik engine produces.

    This bridges the new Drik system into the older session/result format.
    """
    from bheshajpatro.engines.drik import run_daily as drik_daily

    # Compute daily result using Drik engine
    astro = drik_daily(date_ce, place)

    # The Drik daily function should return a "panchanga_result" compatible dict.
    return {
        "context": {
            "date": date_ce,
            "place": place,
            "engine": "drik",
        },
        "products": {
            "main": {
                "panchanga_result": astro,
            }
        },
    }


def build_session(date_ce: date, place: Dict[str, Any], write_csv: bool = False) -> Dict[str, Any]:
    """
    Default pipeline = traditional Ketaki.

    This keeps the signature but avoids importing any missing Ketaki code.
    Instead, it raises a clean error so you know Ketaki is not implemented yet.
    """
    raise NotImplementedError("Ketaki engine is not yet implemented in this build.")
