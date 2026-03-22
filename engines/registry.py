from __future__ import annotations

from datetime import date
from typing import Any, Callable, Dict, Literal

from bheshajpatro.engines.drik.grahas.calc_pday import run as drik_day_run
from bheshajpatro.data.mapnames import get_weekday_name

EngineName = Literal["drik", "ketaki"]


def python_weekday_to_display_id(py_weekday: int) -> int:
    # Python: 0=Mon ... 6=Sun
    # Display: 1=Sun ... 7=Sat
    return ((int(py_weekday) + 1) % 7) + 1


def ketaki_weekday_to_display_id(ketaki_weekday: int) -> int:
    # Assumed ketaki: 0=Wednesday, 1=Thursday, ..., 6=Tuesday
    mapping = {
        0: 4,  # Wednesday
        1: 5,  # Thursday
        2: 6,  # Friday
        3: 7,  # Saturday
        4: 1,  # Sunday
        5: 2,  # Monday
        6: 3,  # Tuesday
    }
    return mapping[int(ketaki_weekday) % 7]


def _ensure_context(
    session: Dict[str, Any],
    *,
    d: date,
    engine: str,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float | None,
    weekday_id: int,
) -> Dict[str, Any]:
    ctx = session.setdefault("context", {})
    ctx["date"] = d.isoformat()
    ctx["engine"] = engine
    ctx["location"] = {
        "latitude": latitude_deg,
        "longitude": longitude_deg,
        "std_meridian": standard_meridian_deg,
        "tz_name": tz_name,
        "elevation": elevation_m or 0.0,
    }
    ctx["weekday_id"] = weekday_id
    ctx["day_name"] = get_weekday_name(weekday_id, "en")
    return session


def run_drik_day(
    d: date,
    latitude_deg: float,
    longitude_deg: float,
    standard_meridian_deg: float,
    tz_name: str | None,
    elevation_m: float | None = 0.0,
) -> Dict[str, Any]:
    session = drik_day_run(
        d,
        latitude_deg,
        longitude_deg,
        standard_meridian_deg,
        tz_name,
        elevation_m,
    )

    weekday_id = python_weekday_to_display_id(d.weekday())

    return _ensure_context(
        session,
        d=d,
        engine="drik",
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        standard_meridian_deg=standard_meridian_deg,
        tz_name=tz_name,
        elevation_m=elevation_m,
        weekday_id=weekday_id,
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
    Placeholder shape for ketaki.

    Later:
      1) civil date -> ahargana
      2) ahargana -> weekday_native
      3) weekday_native -> weekday_id
      4) fill normalized context
    """
    raise NotImplementedError("ketaki engine is not wired yet.")


ENGINE_RUNNERS: dict[str, Callable[..., Dict[str, Any]]] = {
    "drik": run_drik_day,
    "ketaki": run_ketaki_day,
}