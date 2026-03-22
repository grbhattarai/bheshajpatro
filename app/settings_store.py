from __future__ import annotations

from typing import Any, Dict

from starlette.requests import Request

DEFAULT_ENGINE = "drik"

DEFAULT_PLACE: Dict[str, Any] = {
    "key": "kathmandu_np",
    "name": "Kathmandu, Nepal",
    "latitude": 27.7172,
    "longitude": 85.3240,
    "standard": 86.25,
    "tz": "Asia/Kathmandu",
    "elevation": 1300.0,
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