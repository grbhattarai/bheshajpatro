# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later

# Build one-day Drik Panchanga session (engine-agnostic output shape)

from __future__ import annotations

from datetime import date as _date, datetime
from typing import Any, Dict

from bheshajpatro.engines.drik.core.noaa_sunrise import sunset_local
from bheshajpatro.engines.drik.grahas.calc_grahas import daily_grahas, GRAHAS

__all__ = ["build_session", "run"]


def _local_hours(dt: datetime) -> float:
    """
    Convert a (local) datetime to fractional hours since local midnight.
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
    ephe_dir: str | None,
) -> Dict[str, Any]:
    """
    Engine-specific builder, engine-agnostic session output.

    Everything stays snake_case here. Any camelCase conversion for UI
    should happen at the presentation layer, not inside the engine.
    """

    daily = daily_grahas(
        d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        elevation=elevation,
        ephe_dir=ephe_dir,
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
            "graha_spashta": daily.graha_spashta,
            "suryodaya_spashta": daily.suryodaya_spashta,
            "graha_gati": daily.graha_gati,
            "sunrise_hours": sunrise_hours,
            "sunset_hours": sunset_hours,
            "sunrise_local": daily.sunrise.event_local.isoformat(),
            "sunset_local": sunset_event.event_local.isoformat(),
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
    ephe_dir: str | None = None,
) -> Dict[str, Any]:
    """
    Public entry point for one-day Drik panchanga session JSON (snake_case).
    """
    return build_session(
        d=d,
        latitude=latitude,
        longitude=longitude,
        std_meridian=std_meridian,
        tz_name=tz_name,
        elevation=elevation,
        ephe_dir=ephe_dir,
    )


# ----------------------------------------------------------------------
# SIMPLE SELF-TESTS (run: python -m bheshajpatro.engines.drik.grahas.calc_pday)
# ----------------------------------------------------------------------

def _run_self_tests() -> None:
    print("Running calc_pday self-tests...")

    from datetime import date as _d

    # Kathmandu sample: 2025-01-01
    d_test = _d(2025, 1, 1)
    lat_ktm = 27.7172
    lon_ktm = 85.3240
    std_meridian_ktm = 86.25  # UTC+5:45

    session = run(
        d_test,
        latitude=lat_ktm,
        longitude=lon_ktm,
        std_meridian=std_meridian_ktm,
        tz_name="Asia/Kathmandu",
        elevation=1300.0,
        ephe_dir=None,
    )

    print("\n[ session keys ]")
    print("top-level:", list(session.keys()))
    print("context :", session["context"])
    print("astro   keys:", list(session["astro"].keys()))

    # Basic shape checks
    assert "context" in session
    assert "astro" in session

    context = session["context"]
    astro = session["astro"]

    # Context checks
    assert context["date"] == d_test.isoformat()
    loc = context["location"]
    assert loc["latitude"] == float(lat_ktm)
    assert loc["longitude"] == float(lon_ktm)
    assert loc["std_meridian"] == float(std_meridian_ktm)
    assert context["engine"] == "drik"

    # Astro keys present (all snake_case)
    for key in (
        "graha_spashta",
        "suryodaya_spashta",
        "graha_gati",
        "sunrise_hours",
        "sunset_hours",
        "sunrise_local",
        "sunset_local",
    ):
        assert key in astro, f"missing astro key: {key}"

    graha_spashta = astro["graha_spashta"]
    suryodaya_spashta = astro["suryodaya_spashta"]
    graha_gati = astro["graha_gati"]
    sunrise_hours = astro["sunrise_hours"]
    sunset_hours = astro["sunset_hours"]
    sunrise_local = astro["sunrise_local"]
    sunset_local = astro["sunset_local"]

    # --- Expected snapshot values for Kathmandu 2025-01-01 -------------
    expected_graha_spashta = {
        "surya": 256.619996920229,
        "chandra": 270.590632192347,
        "mangal": 97.7054499381971,
        "budha": 235.67891194474979,
        "guru": 49.007576536725715,
        "shukra": 303.5182859693778,
        "shani": 320.3185317651758,
        "rahu": 337.29048531610664,
        "ketu": 157.29048531610655,
    }

    expected_suryodaya_spashta = {
        "surya": 256.6581775990718,
        "chandra": 271.1146406673764,
        "mangal": 97.69295216085874,
        "budha": 235.72698696368874,
        "guru": 49.00363529995037,
        "shukra": 303.5589406286382,
        "shani": 320.3214154124859,
        "rahu": 337.2885002661505,
        "ketu": 157.2885002661504,
    }

    # Sunrise at 06:53:59 local -> fractional hours
    expected_sunrise_hours = 6 + 53 / 60.0 + 59 / 3600.0  # 6.899722...

    # --- Detailed checks for grahas ------------------------------------
    print("\n[ graha_spashta @ 06:00 ]")
    for g in GRAHAS:
        assert g in graha_spashta
        assert g in suryodaya_spashta
        assert g in graha_gati

        lon6 = graha_spashta[g]
        lonsr = suryodaya_spashta[g]
        spd = graha_gati[g]

        print(f"{g:8s}  06:00={lon6:.12f}  sr={lonsr:.12f}  gati={spd:.6f}")

        # Longitudes must be in [0, 360)
        assert 0.0 <= lon6 < 360.0
        assert 0.0 <= lonsr < 360.0

        # Match expected snapshot (tolerance for floating variation)
        diff_6 = abs(lon6 - expected_graha_spashta[g])
        diff_sr = abs(lonsr - expected_suryodaya_spashta[g])
        assert diff_6 < 1e-6, f"{g} 06:00 lon diff too large: {diff_6}"
        assert diff_sr < 1e-6, f"{g} sunrise lon diff too large: {diff_sr}"

        # Speeds should be finite floats
        assert isinstance(spd, float)

    # --- Sunrise / sunset checks ---------------------------------------
    print("\n[ sunrise / sunset ]")
    print("sunrise_hours =", sunrise_hours)
    print("sunset_hours  =", sunset_hours)
    print("sunrise_local =", sunrise_local)
    print("sunset_local  =", sunset_local)

    # Sunrise hours close to expected (within ~0.5 sec)
    assert abs(sunrise_hours - expected_sunrise_hours) < 1e-4

    # Sunrise string should encode 06:53:59
    assert sunrise_local.startswith("2025-01-01T06:53:59")

    # Sunset should be sometime late afternoon / evening local
    assert 16.0 <= sunset_hours <= 20.0

    print("\nAll calc_pday self-tests passed.")


if __name__ == "__main__":
    print("Running calc_pday self-tests from direct execution...\n")
    _run_self_tests()
