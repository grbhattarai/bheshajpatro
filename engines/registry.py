from __future__ import annotations

from datetime import date
from typing import Any, Callable, Dict, Literal

# Drik daily runner (already working)
from bheshajpatro.engines.drik.grahas.calc_pday import run as drik_day_run

EngineName = Literal["drik", "ketaki"]


def run_drik_day(
    d: date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float | None = 0.0,
) -> Dict[str, Any]:
    return drik_day_run(
        d,
        latitude_deg,
        longitude_deg,
        standard_meridian_deg,
        tz_name,
        elevation_m,
    )


def run_ketaki_day(
    d: date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float | None = 0.0,
) -> Dict[str, Any]:
    """
    Placeholder for ketaki.

    Outer contract stays identical to drik:
      input  = civil date + place
      output = normalized engine session dict

    Internally ketaki may do:
      civil date -> ahargana -> graha positions/speeds -> session
    """
    raise NotImplementedError("ketaki engine is not wired yet.")


ENGINE_RUNNERS: dict[str, Callable[..., Dict[str, Any]]] = {
    "drik": run_drik_day,
    "ketaki": run_ketaki_day,
}