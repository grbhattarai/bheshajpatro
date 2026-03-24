from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .astro_backend import AstroBackend
from .visibility import EclipseVisibility, classify_visibility


BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "data" / "ephemeris" / "eclipse_catalog.json"


def load_eclipse_catalog(catalog_path: str | Path | None = None) -> dict[str, Any]:
    """
    Load the generated eclipse catalog JSON.
    """
    path = Path(catalog_path) if catalog_path is not None else CATALOG_PATH

    if not path.is_absolute():
        path = BASE_DIR / path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_eclipse_events_for_year(
    year: int,
    catalog_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Return all eclipse events for a given UTC year from the catalog.
    """
    catalog = load_eclipse_catalog(catalog_path)
    events = catalog.get("events", [])

    year_prefix = f"{year:04d}-"
    return [event for event in events if event["time_utc"].startswith(year_prefix)]


def get_visibility_for_event(
    event: dict[str, Any],
    latitude: float,
    longitude: float,
    elevation_m: float = 0.0,
    backend: AstroBackend | None = None,
) -> EclipseVisibility:
    """
    Compute simple location-based visibility for one catalog event.
    """
    if backend is None:
        backend = AstroBackend()

    time_utc = datetime.fromisoformat(event["time_utc"])

    return classify_visibility(
        backend=backend,
        event_type=event["type"],
        time_utc=time_utc,
        latitude=latitude,
        longitude=longitude,
        elevation_m=elevation_m,
    )


def _get_visibility_status(event_type: str, visibility: EclipseVisibility) -> str:
    """
    Return a short UI-friendly visibility label.
    """
    if event_type == "lunar":
        return "visible" if visibility.visible else "not_visible"

    if event_type == "solar":
        return "daylight_possible" if visibility.visible else "not_visible"

    return "unknown"


def get_eclipse_year_report(
    year: int,
    latitude: float,
    longitude: float,
    elevation_m: float = 0.0,
    catalog_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Return a year report combining catalog event data with simple visibility.

    Each item includes:
    - original catalog fields
    - sun_alt_deg
    - moon_alt_deg
    - visible
    - visibility_note
    - visibility_status
    """
    backend = AstroBackend()
    events = get_eclipse_events_for_year(year, catalog_path=catalog_path)

    report: list[dict[str, Any]] = []

    for event in events:
        visibility = get_visibility_for_event(
            event=event,
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation_m,
            backend=backend,
        )

        report.append(
            {
                **event,
                "sun_alt_deg": round(visibility.sun_alt_deg, 6),
                "moon_alt_deg": round(visibility.moon_alt_deg, 6),
                "visible": bool(visibility.visible),
                "visibility_note": visibility.visibility_note,
                "visibility_status": _get_visibility_status(event["type"], visibility),
            }
        )

    return report