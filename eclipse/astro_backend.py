from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame


BASE_DIR = Path(__file__).resolve().parent.parent
EPHEMERIS_PATH = BASE_DIR / "data" / "ephemeris" / "de440s.bsp"


class AstroBackend:
    def __init__(self) -> None:
        self.ts = load.timescale()
        self.eph = load(str(EPHEMERIS_PATH))

        self.earth = self.eph["earth"]
        self.sun = self.eph["sun"]
        self.moon = self.eph["moon"]

    def _to_time(self, dt: datetime):
        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        return self.ts.from_datetime(dt.astimezone(timezone.utc))

    def get_ecliptic_coords(self, dt: datetime) -> tuple[float, float, float]:
        """
        Returns:
            (sun_lon_deg, moon_lon_deg, moon_lat_deg)
        """
        t = self._to_time(dt)

        earth_at_t = self.earth.at(t)

        sun_app = earth_at_t.observe(self.sun).apparent()
        moon_app = earth_at_t.observe(self.moon).apparent()

        _, sun_lon, _ = sun_app.frame_latlon(ecliptic_frame)
        moon_lat, moon_lon, _ = moon_app.frame_latlon(ecliptic_frame)

        return (
            sun_lon.degrees % 360.0,
            moon_lon.degrees % 360.0,
            moon_lat.degrees,
        )

    def get_altitudes(
        self,
        dt: datetime,
        latitude: float,
        longitude: float,
        elevation_m: float = 0.0,
    ) -> tuple[float, float]:
        """
        Returns:
            (sun_alt_deg, moon_alt_deg)

        Altitudes are topocentric apparent altitudes for the given location.
        """
        t = self._to_time(dt)

        observer = self.earth + wgs84.latlon(
            latitude_degrees=latitude,
            longitude_degrees=longitude,
            elevation_m=elevation_m,
        )

        apparent_sun = observer.at(t).observe(self.sun).apparent()
        apparent_moon = observer.at(t).observe(self.moon).apparent()

        sun_alt, _, _ = apparent_sun.altaz()
        moon_alt, _, _ = apparent_moon.altaz()

        return sun_alt.degrees, moon_alt.degrees