from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class EclipseVisibility:
    event_type: Literal["solar", "lunar"]
    time_utc: datetime
    latitude: float
    longitude: float
    elevation_m: float
    sun_alt_deg: float
    moon_alt_deg: float
    visible: bool
    visibility_note: str


def classify_visibility(
    backend,
    event_type: Literal["solar", "lunar"],
    time_utc: datetime,
    latitude: float,
    longitude: float,
    elevation_m: float = 0.0,
) -> EclipseVisibility:
    """
    Version 1 visibility logic:

    - lunar eclipse:
        visible if Moon is above horizon at event time

    - solar eclipse:
        daylight-possible if Sun is above horizon at event time
        (this does NOT yet confirm that the eclipse path crosses the location)
    """
    sun_alt_deg, moon_alt_deg = backend.get_altitudes(
        dt=time_utc,
        latitude=latitude,
        longitude=longitude,
        elevation_m=elevation_m,
    )

    if event_type == "lunar":
        visible = bool(moon_alt_deg > 0.0)
        if visible:
            note = "Moon above horizon"
        else:
            note = "Moon below horizon"

    elif event_type == "solar":
        visible = bool(sun_alt_deg > 0.0)
        if visible:
            note = "Sun above horizon; local solar path not yet checked"
        else:
            note = "Sun below horizon"

    else:
        raise ValueError("event_type must be 'solar' or 'lunar'")

    return EclipseVisibility(
        event_type=event_type,
        time_utc=time_utc,
        latitude=float(latitude),
        longitude=float(longitude),
        elevation_m=float(elevation_m),
        sun_alt_deg=float(sun_alt_deg),
        moon_alt_deg=float(moon_alt_deg),
        visible=visible,
        visibility_note=note,
    )