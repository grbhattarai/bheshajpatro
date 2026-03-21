# bheshajpatro/utils/validation.py
from __future__ import annotations

from datetime import date
from typing import Dict, Any
from bheshajpatro.utils.exceptions import ValidationError


def validate_lat(lat: float) -> float:
    if not (-90.0 <= lat <= 90.0):
        raise ValidationError(f"Invalid latitude: {lat}")
    return float(lat)


def validate_lon(lon: float) -> float:
    if not (-180.0 <= lon <= 180.0):
        raise ValidationError(f"Invalid longitude: {lon}")
    return float(lon)


def validate_standard_meridian(std: float) -> float:
    # Not strict — many countries use non-ideal meridians.
    return float(std)


def validate_place(place: Dict[str, Any]) -> Dict[str, Any]:
    if "latitude" in place:
        place["latitude"] = validate_lat(place["latitude"])
    if "longitude" in place:
        place["longitude"] = validate_lon(place["longitude"])
    if "standard" in place:
        place["standard"] = validate_standard_meridian(place["standard"])
    return place


def validate_date(d: date) -> date:
    if not isinstance(d, date):
        raise ValidationError(f"Invalid date: {d}")
    return d
