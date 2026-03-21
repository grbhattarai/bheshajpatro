# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

# Build one-day Drik Panchanga session (engine-agnostic output shape)

from __future__ import annotations

# =============================================================================
# DEV OVERRIDE (REMOVE AFTER TESTING)
# -----------------------------------------------------------------------------
# Allows direct execution:
#     python engines/drik/grahas/calc_pday.py
# =============================================================================
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path

    PACKAGE_PARENT = Path(__file__).resolve().parents[4]
    if str(PACKAGE_PARENT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_PARENT))
# =============================================================================

from datetime import date as _date, datetime
from typing import Any, Dict

from bheshajpatro.engines.drik.core.noaa_sunrise import sunset_local
from bheshajpatro.engines.drik.grahas.calc_grahas import daily_grahas, GRAHAS

__all__ = ["build_session", "run"]


def _local_hours(dt: datetime) -> float:
    """
    Convert a local datetime to fractional hours since local midnight.
    """
    return (
        dt.hour
        + dt.minute / 60.0
        + dt.second / 3600.0
        + dt.microsecond / 3_600_000_000.0
    )


def build_session(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None,
    elevation: float | None,
) -> Dict[str, Any]:
    """
    Engine-specific builder, engine-agnostic session output.

    Everything stays snake_case here. Any camelCase conversion for UI
    should happen at the presentation layer, not inside the engine.

    Sunrise values are the primary Panchanga anchor.
    """

    daily = daily_grahas(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        elevation=elevation,
        use_topocentric=True,
    )

    sunset_event = sunset_local(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
    )

    sunrise_hours = _local_hours(daily.sunrise.event_local)
    sunset_hours = _local_hours(sunset_event.event_local)

    session: Dict[str, Any] = {
        "context": {
            "date": d.isoformat(),
            "location": {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "std_meridian": float(std_meridian),
                "tz_name": tz_name,
                "elevation": float(elevation or 0.0),
            },
            "engine": "drik",
        },
        "astro": {
            # Sunrise = primary Panchanga anchor
            "suryodaya_spashta": daily.suryodaya_spashta,
            "suryodaya_gati": daily.suryodaya_gati,
            # 06:00 = reference / migration bridge
            "graha_spashta_6": daily.graha_spashta_6,
            "graha_gati_6": daily.graha_gati_6,
            # Event timing
            "sunrise_hours": sunrise_hours,
            "sunset_hours": sunset_hours,
            "sunrise_local": daily.sunrise.event_local.isoformat(),
            "sunset_local": sunset_event.event_local.isoformat(),
            "jd_ut_sunrise": daily.jd_ut_sunrise,
            "jd_ut_6": daily.jd_ut_6,
        },
    }

    return session


def run(
    d: _date,
    latitude: float,
    longitude: float,
    std_meridian: float,
    tz_name: str | None = None,
    elevation: float | None = 0.0,
) -> Dict[str, Any]:
    """
    Public entry point for one-day Drik Panchanga session JSON (snake_case).
    """
    return build_session(
        d=d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        tz_name=tz_name,
        elevation=elevation,
    )


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running calc_pday self-tests...")

    from datetime import date as _d

    d_test = _d(2025, 1, 1)
    lat_ktm = 27.7172
    lon_ktm = 85.3240
    std_meridian_ktm = 86.25

    session = run(
        d_test,
        latitude=lat_ktm,
        longitude=lon_ktm,
        std_meridian=std_meridian_ktm,
        tz_name="Asia/Kathmandu",
        elevation=1300.0,
    )

    print("\n[ session keys ]")
    print("top-level :", list(session.keys()))
    print("context   :", session["context"])
    print("astro keys:", list(session["astro"].keys()))

    assert "context" in session
    assert "astro" in session

    context = session["context"]
    astro = session["astro"]

    assert context["date"] == d_test.isoformat()
    loc = context["location"]
    assert loc["latitude"] == float(lat_ktm)
    assert loc["longitude"] == float(lon_ktm)
    assert loc["std_meridian"] == float(std_meridian_ktm)
    assert loc["tz_name"] == "Asia/Kathmandu"
    assert context["engine"] == "drik"

    for key in (
        "suryodaya_spashta",
        "suryodaya_gati",
        "graha_spashta_6",
        "graha_gati_6",
        "sunrise_hours",
        "sunset_hours",
        "sunrise_local",
        "sunset_local",
        "jd_ut_sunrise",
        "jd_ut_6",
    ):
        assert key in astro, f"missing astro key: {key}"

    suryodaya_spashta = astro["suryodaya_spashta"]
    suryodaya_gati = astro["suryodaya_gati"]
    graha_spashta_6 = astro["graha_spashta_6"]
    graha_gati_6 = astro["graha_gati_6"]
    sunrise_hours = astro["sunrise_hours"]
    sunset_hours = astro["sunset_hours"]
    sunrise_local = astro["sunrise_local"]
    sunset_local = astro["sunset_local"]

    print("\n[ sunrise anchor grahas ]")
    for g in GRAHAS:
        assert g in suryodaya_spashta
        assert g in suryodaya_gati
        assert g in graha_spashta_6
        assert g in graha_gati_6

        lon_sr = suryodaya_spashta[g]
        gati_sr = suryodaya_gati[g]
        lon_6 = graha_spashta_6[g]
        gati_6 = graha_gati_6[g]

        print(
            f"{g:8s}  sunrise={lon_sr:.12f}  "
            f"gati_sr={gati_sr:.6f}  "
            f"06:00={lon_6:.12f}  gati_6={gati_6:.6f}"
        )

        assert 0.0 <= lon_sr < 360.0
        assert 0.0 <= lon_6 < 360.0
        assert isinstance(gati_sr, float)
        assert isinstance(gati_6, float)

    rahu_lon = suryodaya_spashta["rahu"]
    ketu_lon = suryodaya_spashta["ketu"]
    expected_ketu = (rahu_lon + 180.0) % 360.0
    delta = (ketu_lon - expected_ketu + 180.0) % 360.0 - 180.0
    diff = abs(delta)

    print("\n[ Rahu/Ketu @ sunrise ]")
    print("rahu_lon =", rahu_lon)
    print("ketu_lon =", ketu_lon)
    print("expected ketu_lon ≈", expected_ketu)
    print("angular diff       =", diff)

    assert diff < 1e-3

    print("\n[ sunrise / sunset ]")
    print("sunrise_hours =", sunrise_hours)
    print("sunset_hours  =", sunset_hours)
    print("sunrise_local =", sunrise_local)
    print("sunset_local  =", sunset_local)

    assert sunrise_local.startswith("2025-01-01T06:53:59")
    assert 5.0 <= sunrise_hours <= 8.0
    assert 16.0 <= sunset_hours <= 20.0

    print("\nAll calc_pday self-tests passed.")


if __name__ == "__main__":
    print("Running calc_pday self-tests from direct execution...\n")
    _run_self_tests()