from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class Place(BaseModel):
    """
    Generic place model used across Panchanga and eclipse flows.
    """
    location_key: str
    city: str
    state: str = ""
    country: str

    country_code: str
    state_code: str = ""
    country_code_iso3: str = ""

    latitude: float
    longitude: float

    standard_meridian: float = Field(
        ...,
        description="Standard meridian in degrees, e.g. -75 for EST",
    )
    tz: str


class PanchangaRequest(BaseModel):
    """
    User request for Panchanga computation.
    """
    date: date
    place: Place
    method: Literal["drik", "ketaki", "surya"]


class EclipseRequest(BaseModel):
    """
    User request for eclipse computation.
    Eclipse depends on location and date/year, but not Panchanga method.
    """
    date: date
    place: Place


class PanchangaContext(BaseModel):
    """
    Computation context returned by the engine/service layer.
    """
    date: date
    place: Place
    method: Literal["drik", "ketaki", "surya"]
    standard_offset_hours: float


class PanchangaResult(BaseModel):
    """
    Final built daily Panchanga result, engine-agnostic.

    Fields remain optional during migration so partial data does not
    break the whole pipeline. Extra fields are allowed so engines or
    builders can evolve without immediate schema failures.
    """
    model_config = ConfigDict(extra="allow")

    ahargana: int | None = None
    chandra_degree: float | None = None
    date_ce: str | None = None
    day_name: str | None = None
    day_nbr: float | None = None
    dinamana_dec: float | None = None
    dinmana: str | None = None
    month_name: str | None = None
    moon_rashi: int | None = None
    naksha_hm: str | None = None
    nakshatra: int | None = None
    nakshatra_gp: str | None = None
    nakshatra_name: str | None = None
    rashi_name: str | None = None
    sun_day: int | None = None
    sun_rashi: int | None = None
    sunrise: str | None = None
    sunset: str | None = None
    surya_degree: float | None = None
    tithi: int | None = None
    tithi_gp: str | None = None
    tithi_hm: str | None = None
    tithi_name: str | None = None
    yoga: int | None = None
    yoga_gp: str | None = None
    yoga_hm: str | None = None
    yoga_name: str | None = None


class EclipseResult(BaseModel):
    """
    Placeholder result model for eclipse pages.
    Keep flexible for now until eclipse output structure stabilizes.
    """
    model_config = ConfigDict(extra="allow")