# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from bheshajpatro.utils.paths import input_data_path

__all__ = [
    "WORLD_CITIES_CSV_NAME",
    "DEFAULT_WORLD_CITIES_PATH",
    "City",
    "all_cities",
    "search_cities",
    "get_city",
    "get_location_key",
    "get_city_by_location_key",
]


WORLD_CITIES_CSV_NAME = "worldcities.csv"
DEFAULT_WORLD_CITIES_PATH = Path(input_data_path(WORLD_CITIES_CSV_NAME))


# ---------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------

def _norm_text(value: str | None) -> str:
    """
    Normalize city names.

    Examples:
        "New York" -> "new_york"
        "St. John's" -> "st_johns"
    """
    s = (value or "").strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s.strip("_")


def _norm_code(value: str | None) -> str:
    """
    Normalize country/state codes to lowercase.
    """
    return (value or "").strip().lower()


# ---------------------------------------------------------------------
# Location Key
# ---------------------------------------------------------------------

def build_location_key(
    country_code: str,
    city: str,
    state_code: str = "",
) -> str:
    """
    Canonical lowercase location key.

    Format:
        countrycode_statecode_city
        OR
        countrycode_city

    Examples:
        af_kabul
        mx_jal_guadalajara
        ca_bc_vancouver
    """
    cc = _norm_code(country_code)
    sc = _norm_code(state_code)
    city_part = _norm_text(city)

    parts = [cc]
    if sc:
        parts.append(sc)
    if city_part:
        parts.append(city_part)

    return "_".join(parts)


# ---------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class City:
    country: str
    state: str
    city: str
    latitude: float
    longitude: float
    standard: float
    tz: str
    country_code: str
    state_code: str
    country_code_iso3: str
    location_key: str

    @property
    def label(self) -> str:
        parts = [self.city.title()]
        if self.state.strip():
            parts.append(self.state.title())
        parts.append(self.country.title())
        return ", ".join(parts)

    @property
    def canonical_place(self) -> dict[str, Any]:
        return {
            "city": self.city.strip().lower(),
            "state": self.state.strip().lower(),
            "country": self.country.strip().lower(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "standard": self.standard,
            "tz": self.tz.strip(),
            "country_code": self.country_code.strip().upper(),
            "state_code": self.state_code.strip().upper(),
            "country_code_iso3": self.country_code_iso3.strip().upper(),
            "location_key": self.location_key,
        }


# ---------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------

@lru_cache(maxsize=4)
def all_cities(csv_path: str | Path | None = None) -> tuple[City, ...]:
    path = Path(csv_path) if csv_path else DEFAULT_WORLD_CITIES_PATH

    cities: list[City] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            location_key = build_location_key(
                country_code=row.get("country_code"),
                state_code=row.get("state_code"),
                city=row.get("city"),
            )

            cities.append(
                City(
                    country=(row.get("country") or "").strip(),
                    state=(row.get("state") or "").strip(),
                    city=(row.get("city") or "").strip(),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    standard=float(row["standard"]),
                    tz=(row.get("tz") or "").strip(),
                    country_code=(row.get("country_code") or "").strip(),
                    state_code=(row.get("state_code") or "").strip(),
                    country_code_iso3=(row.get("country_code_iso3") or "").strip(),
                    location_key=location_key,
                )
            )

    return tuple(cities)


@lru_cache(maxsize=4)
def _location_key_index(csv_path: str | Path | None = None) -> dict[str, City]:
    index: dict[str, City] = {}

    for c in all_cities(csv_path):
        if c.location_key in index:
            raise ValueError(f"duplicate location_key: {c.location_key}")
        index[c.location_key] = c

    return index


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def search_cities(query: str, limit: int = 15) -> list[City]:
    q = query.strip().lower()
    if not q:
        return []

    return [
        c for c in all_cities()
        if q in c.label.lower() or q in c.location_key
    ][:limit]


def get_location_key(
    country_code: str,
    city: str,
    state_code: str | None = None,
) -> str:
    return build_location_key(
        country_code=country_code,
        state_code=state_code or "",
        city=city,
    )


def get_city_by_location_key(location_key: str) -> City:
    key = location_key.strip().lower()
    try:
        return _location_key_index()[key]
    except KeyError as exc:
        raise KeyError(f"location_key not found: {location_key!r}") from exc


def get_city(
    city: str,
    country: str | None = None,
    state: str | None = None,
) -> City:
    city_norm = city.strip().lower()
    country_norm = country.strip().lower() if country else None
    state_norm = state.strip().lower() if state else None

    cities = all_cities()

    if country_norm is not None and state_norm is not None:
        for c in cities:
            if (
                c.city.strip().lower() == city_norm
                and c.country.strip().lower() == country_norm
                and c.state.strip().lower() == state_norm
            ):
                return c

    if country_norm is not None:
        for c in cities:
            if (
                c.city.strip().lower() == city_norm
                and c.country.strip().lower() == country_norm
            ):
                return c

    for c in cities:
        if c.city.strip().lower() == city_norm:
            return c

    raise KeyError(f"city not found: {city!r} country={country!r} state={state!r}")