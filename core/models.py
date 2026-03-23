# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import datetime as dt
from typing import Literal, Any, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class Place(BaseModel):
    """
    Generic place model used across Panchanga and eclipse flows.
    """
    model_config = ConfigDict(populate_by_name=True)

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
        alias="standard",
        description="Standard meridian in degrees, e.g. -75 for EST",
    )
    tz: str


class PanchangaRequest(BaseModel):
    """
    User request for Panchanga computation.
    """
    date: dt.date
    place: Place
    method: Literal["drik", "ketaki"]


class EclipseRequest(BaseModel):
    """
    User request for eclipse computation.
    Eclipse depends on location and date/year, but not Panchanga method.
    """
    date: dt.date
    place: Place


class PanchangaContext(BaseModel):
    """
    Computation context returned by the engine/service layer.
    """
    model_config = ConfigDict(extra="allow")

    date: Optional[dt.date] = None
    place: Optional[Union[Place, dict[str, Any]]] = None
    method: Optional[Literal["drik", "ketaki"]] = None
    standard_offset_hours: Optional[float] = None


class PanchangaResult(BaseModel):
    """
    Final built daily Panchanga result, engine-agnostic.

    Extra fields are allowed during migration so the pipeline remains stable.

    TODO: add when compute engine supports them:
        samvatsara, samvatsara_name
        vikram_samvat
        masa_name
        ritu, ritu_name
        shivavas, agnivasa, brahmavas
    """
    model_config = ConfigDict(extra="allow")

    ahargana: Optional[int] = None

    date_ce: Optional[str] = None
    date_bs: Optional[str] = None
    bs_year: Optional[int] = None
    shaka_year: Optional[int] = None

    day_name: Optional[str] = None
    day_nbr: Optional[float] = None
    paksha: Optional[str] = None

    emonth: Optional[int] = None
    emonth_name: Optional[str] = None
    nmonth: Optional[int] = None
    nmonth_name: Optional[str] = None

    tithi1: Optional[int] = None
    tithi1_gp: Optional[str] = None
    tithi1_hm: Optional[str] = None
    tithi1_name: Optional[str] = None

    tithi2: Optional[int] = None
    tithi2_hm: Optional[str] = None
    tithi2_name: Optional[str] = None

    tithi3: Optional[int] = None
    tithi3_hm: Optional[str] = None
    tithi3_name: Optional[str] = None

    nakshatra1: Optional[int] = None
    nakshatra1_gp: Optional[str] = None
    nakshatra1_hm: Optional[str] = None
    nakshatra1_name: Optional[str] = None

    nakshatra2: Optional[int] = None
    nakshatra2_hm: Optional[str] = None
    nakshatra2_name: Optional[str] = None

    nakshatra3: Optional[int] = None
    nakshatra3_hm: Optional[str] = None
    nakshatra3_name: Optional[str] = None

    surya_nakshatra1: Optional[int] = None
    surya_nakshatra1_gp: Optional[str] = None
    surya_nakshatra1_hm: Optional[str] = None
    surya_nakshatra1_name: Optional[str] = None

    surya_nakshatra2: Optional[int] = None
    surya_nakshatra2_hm: Optional[str] = None
    surya_nakshatra2_name: Optional[str] = None

    yoga1: Optional[int] = None
    yoga1_gp: Optional[str] = None
    yoga1_hm: Optional[str] = None
    yoga1_name: Optional[str] = None

    yoga2: Optional[int] = None
    yoga2_hm: Optional[str] = None
    yoga2_name: Optional[str] = None

    yoga3: Optional[int] = None
    yoga3_hm: Optional[str] = None
    yoga3_name: Optional[str] = None

    karana1: Optional[int] = None
    karana1_hm: Optional[str] = None
    karana1_name: Optional[str] = None

    karana2: Optional[int] = None
    karana2_hm: Optional[str] = None
    karana2_name: Optional[str] = None

    karana3: Optional[int] = None
    karana3_hm: Optional[str] = None
    karana3_name: Optional[str] = None

    karana4: Optional[int] = None
    karana4_hm: Optional[str] = None
    karana4_name: Optional[str] = None

    sun_degree: Optional[float] = None
    sun_rashi1: Optional[int] = None
    sun_rashi1_name: Optional[str] = None

    moon_degree: Optional[float] = None
    moon_rashi1: Optional[int] = None
    moon_rashi1_name: Optional[str] = None
    moon_rashi1_hm: Optional[str] = None

    moon_rashi2: Optional[int] = None
    moon_rashi2_name: Optional[str] = None

    dinamana_hm: Optional[str] = None
    dinamana_gp: Optional[str] = None
    dinamana_dec: Optional[float] = None

    sunrise_hm: Optional[str] = None
    sunset_hm: Optional[str] = None
    sunrise_dec: Optional[float] = None
    sunset_dec: Optional[float] = None
    dst_hours: Optional[float] = None

    sun_day: Optional[int] = None


class PanchangaResponse(BaseModel):
    """
    Full Panchanga API/service response.
    """
    model_config = ConfigDict(extra="allow")

    context: dict[str, Any]
    result: PanchangaResult


class EclipseResult(BaseModel):
    """
    Placeholder result model for eclipse pages.
    Keep flexible for now until eclipse output structure stabilizes.
    """
    model_config = ConfigDict(extra="allow")