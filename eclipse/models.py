from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EclipseEvent:
    kind: str  # "solar" | "lunar"
    eclipse_type: str  # "total" | "partial" | "annular" | "penumbral"
    global_date: str  # YYYY-MM-DD
    title: str

    visible: bool
    visibility_note: str

    start_local: Optional[str] = None
    maximum_local: Optional[str] = None
    end_local: Optional[str] = None

    magnitude: Optional[float] = None
    obscuration: Optional[float] = None

    tithi: Optional[str] = None
    nakshatra: Optional[str] = None
    sutak_start: Optional[str] = None

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EclipseYearReport:
    place_key: str
    place_name: str
    year: int

    total_events: int
    visible_events: int
    solar_count: int
    lunar_count: int

    events: List[EclipseEvent]
    graphics: Dict[str, Any] = field(default_factory=dict)