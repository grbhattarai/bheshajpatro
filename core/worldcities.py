# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import csv
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
]


DEFAULT_WORLD_CITIES_PATH = input_data_path("worldcities.csv")


@dataclass
class City:
    country: str   # as in CSV
    state: str
    city: str
    latitude: float
    longitude: float
    standard: float
    tz: str

    @property
    def label_city(self) -> str:
        return self.city.strip().title()

    @property
    def label_state(self) -> str:
        return self.state.strip().title()

    @property
    def label_country(self) -> str:
        return self.country.strip().title()

    @property
    def label(self) -> str:
        """
        Full label for dropdown: "City, State, Country"
        (State omitted if blank).
        """
        parts = [self.label_city]
        if self.state.strip():
            parts.append(self.label_state)
        parts.append(self.label_country)
        return ", ".join(parts)

    @property
    def canonical_place(self) -> dict[str, Any]:
        """
        Canonical lowercase place dict for the backend.
        """
        return {
            "city": self.city.strip().lower(),
            "state": self.state.strip().lower(),
            "country": self.country.strip().lower(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "standard": self.standard,
            "tz": self.tz.strip().lower(),
        }


# ---------------------------------------------------------------------
# Loading and lookup
# ---------------------------------------------------------------------


@lru_cache(maxsize=1)
def all_cities(csv_path: str | Path | None = None) -> list[City]:
    """
    Load all cities from the CSV. Cached (single load per process).
    """
    path = Path(csv_path) if csv_path is not None else DEFAULT_WORLD_CITIES_PATH

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            City(
                country=row["country"],
                state=row["state"],
                city=row["city"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                standard=float(row["standard"]),
                tz=row["tz"],
            )
            for row in reader
        ]


def search_cities(query: str, limit: int = 15) -> list[City]:
    """
    Case-insensitive search over 'City, State, Country'.
    """
    q = query.strip().lower()
    if not q:
        return []

    def _match(c: City) -> bool:
        return q in c.label.lower()

    results = [c for c in all_cities() if _match(c)]
    return results[:limit]


def get_city(
    city: str,
    country: str | None = None,
    state: str | None = None,
) -> City:
    """
    Convenience lookup for a single city.

    Priority:
      1) city + country + state
      2) city + country
      3) city only (first match)
    """
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


if __name__ == "__main__":
    print(f"using csv: {DEFAULT_WORLD_CITIES_PATH}")
    cities = all_cities()
    print(f"loaded {len(cities)} cities\n")

    for c in cities[:10]:
        print(
            f"{c.label:40s}  "
            f"lat={c.latitude:8.4f}  lon={c.longitude:9.4f}  "
            f"standard={c.standard:6.1f}  tz={c.tz}"
        )
