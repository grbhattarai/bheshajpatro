import json
from datetime import datetime, timezone
from pathlib import Path

from astro_backend import AstroBackend
from calculator import find_eclipses_for_year


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "data" / "ephemeris" / "eclipse_catalog.json"


def serialize_candidate(c):
    return {
        "time_utc": c.time_utc.isoformat(),
        "type": c.kind,
        "phase_deg": round(c.phase_deg, 6),
        "moon_lat_deg": round(c.moon_lat_deg, 6),
        "sun_lon_deg": round(c.sun_lon_deg, 6),
        "moon_lon_deg": round(c.moon_lon_deg, 6),
    }


def build_catalog(
    start_year: int = 1849,
    end_year: int = 2150,
    output_path: str | Path | None = None,
):
    backend = AstroBackend()

    if output_path is None:
        output_file = DEFAULT_OUTPUT_PATH
    else:
        output_file = Path(output_path)

        # If caller passes a relative path, resolve it from project root.
        if not output_file.is_absolute():
            output_file = BASE_DIR / output_file

    output_file.parent.mkdir(parents=True, exist_ok=True)

    all_events = []

    print(f"Building eclipse catalog: {start_year} → {end_year}")

    for year in range(start_year, end_year + 1):
        print(f"{year} ({year - start_year + 1}/{end_year - start_year + 1})")

        events = find_eclipses_for_year(backend, year)

        for e in events:
            all_events.append(serialize_candidate(e))

    catalog = {
        "catalog_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ephemeris": "de440s.bsp",
        "start_year": start_year,
        "end_year": end_year,
        "event_count": len(all_events),
        "events": all_events,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"\nDone. Total events: {len(all_events)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    build_catalog(2001, 2100)
