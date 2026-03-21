# bheshajpatro/core/models.py

from datetime import date
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class Place(BaseModel):
    """
    Generic place model used across the Panchanga stack.
    """
    city: str
    state: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    standard: float = Field(..., description="Standard meridian (e.g. -75 for EST)")
    tz: str


class PanchangaContext(BaseModel):
    """
    Additional context returned by the engine session.
    The schema is intentionally loose so you can evolve it.
    """
    date: date
    place: Place
    standard_offset_hours: float


class PanchangaResult(BaseModel):
    """
    One daily Panchanga row, engine-agnostic.

    IMPORTANT:
    - All fields are OPTIONAL so we don't get 500s if the engine
      omits some of them (e.g. ahargana).
    - `extra="allow"` lets the engine return additional keys
      without breaking the API.
    """
    model_config = ConfigDict(extra="allow")

    ahargana: Optional[int] = None
    chandra_degree: Optional[float] = None
    date_ce: Optional[str] = None
    day_name: Optional[str] = None
    day_nbr: Optional[float] = None
    dinamana_dec: Optional[float] = None
    dinmana: Optional[str] = None
    month_name: Optional[str] = None
    moon_rashi: Optional[int] = None
    naksha_hm: Optional[str] = None
    nakshatra: Optional[int] = None
    nakshatra_gp: Optional[str] = None
    nakshatra_name: Optional[str] = None
    rashi_name: Optional[str] = None
    sun_day: Optional[int] = None
    sun_rashi: Optional[int] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    surya_degree: Optional[float] = None
    tithi: Optional[int] = None
    tithi_gp: Optional[str] = None
    tithi_hm: Optional[str] = None
    tithi_name: Optional[str] = None
    yoga: Optional[int] = None
    yoga_gp: Optional[str] = None
    yoga_hm: Optional[str] = None
    yoga_name: Optional[str] = None


class PanchangaResponse(BaseModel):
    """
    High-level response from /bheshajpatro/daily.

    We keep this flexible:
    - context: optional dict
    - result: PanchangaResult or omitted
    - panchanga_result: also allowed, so pengines that use
      'panchanga_result' instead of 'result' still validate.
    - extra="allow" so other top-level keys are fine.
    """
    model_config = ConfigDict(extra="allow")

    context: Optional[Dict[str, Any]] = None
    result: Optional[PanchangaResult] = None
    panchanga_result: Optional[PanchangaResult] = None
