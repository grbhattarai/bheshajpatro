from __future__ import annotations

from typing import Any, Dict

from starlette.requests import Request

DEFAULT_ENGINE = "drik"

DEFAULT_PLACE: Dict[str, Any] = {
    "key": "raleigh_nc_us",
    "name": "Raleigh, NC, USA",
    "latitude": 35.7796,
    "longitude": -78.6382,
    "standard": -300.0,   # UTC-5 (EST) in minutes, or however you store offset
    "tz": "America/New_York",
    "elevation": 96.0,
}


def load_user_settings(request: Request) -> Dict[str, Any]:
    return {
        "engine": request.session.get("engine", DEFAULT_ENGINE),
        "place": request.session.get("place", DEFAULT_PLACE),
    }


def save_user_settings(request: Request, engine: str, place: Dict[str, Any]) -> None:
    request.session["engine"] = engine
    request.session["place"] = place


def clear_user_settings(request: Request) -> None:
    request.session.pop("engine", None)
    request.session.pop("place", None)