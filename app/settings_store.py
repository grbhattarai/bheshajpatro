from __future__ import annotations

from typing import Any, Dict

from starlette.requests import Request

ALLOWED_ENGINES = {"drik", "ketaki"}
DEFAULT_ENGINE = "drik"

DEFAULT_PLACE: Dict[str, Any] = {
    "key": "raleigh_nc_us",
    "name": "Raleigh, NC, USA",
    "latitude": 35.7796,
    "longitude": -78.6382,
    "std_meridian": -75.0,
    "tz_name": "America/New_York",
    "elevation": 96.0,
}


def _normalize_engine(engine: Any) -> str:
    return engine if engine in ALLOWED_ENGINES else DEFAULT_ENGINE


def _normalize_place(place: Dict[str, Any]) -> Dict[str, Any]:
    if not place:
        return dict(DEFAULT_PLACE)

    normalized = dict(place)

    if "tz_name" not in normalized and "tz" in normalized:
        normalized["tz_name"] = normalized["tz"]

    if "std_meridian" not in normalized and "standard" in normalized:
        normalized["std_meridian"] = normalized["standard"]

    normalized.setdefault("key", DEFAULT_PLACE["key"])
    normalized.setdefault("name", DEFAULT_PLACE["name"])
    normalized.setdefault("latitude", DEFAULT_PLACE["latitude"])
    normalized.setdefault("longitude", DEFAULT_PLACE["longitude"])
    normalized.setdefault("std_meridian", DEFAULT_PLACE["std_meridian"])
    normalized.setdefault("tz_name", DEFAULT_PLACE["tz_name"])
    normalized.setdefault("elevation", DEFAULT_PLACE["elevation"])

    return normalized


def load_user_settings(request: Request) -> Dict[str, Any]:
    return {
        "engine": _normalize_engine(request.session.get("engine", DEFAULT_ENGINE)),
        "place": _normalize_place(request.session.get("place", DEFAULT_PLACE)),
    }


def save_user_settings(request: Request, engine: str, place: Dict[str, Any]) -> None:
    request.session["engine"] = _normalize_engine(engine)
    request.session["place"] = _normalize_place(place)


def clear_user_settings(request: Request) -> None:
    request.session.pop("engine", None)
    request.session.pop("place", None)