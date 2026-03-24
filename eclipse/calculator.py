from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal


@dataclass(frozen=True)
class EclipseCandidate:
    kind: Literal["solar", "lunar"]
    time_utc: datetime
    phase_deg: float
    moon_lat_deg: float
    sun_lon_deg: float
    moon_lon_deg: float


def phase_angle_deg(sun_lon: float, moon_lon: float) -> float:
    """
    Return Moon-Sun ecliptic longitude difference in degrees,
    normalized to the range [0, 360).
    """
    return (moon_lon - sun_lon) % 360.0


def is_near_new_moon(phase_deg: float, orb_deg: float = 15.0) -> bool:
    """
    New moon means phase is near 0 degrees.

    Because phase is normalized to [0, 360), values near 360 degrees
    are also effectively near 0 degrees.
    """
    return phase_deg <= orb_deg or phase_deg >= (360.0 - orb_deg)


def is_near_full_moon(phase_deg: float, orb_deg: float = 15.0) -> bool:
    """
    Full moon means phase is near 180 degrees.
    """
    return abs(phase_deg - 180.0) <= orb_deg


def phase_distance_for_kind(kind: Literal["solar", "lunar"], phase_deg: float) -> float:
    """
    Distance from exact target phase:
    - solar -> 0°
    - lunar -> 180°
    """
    if kind == "solar":
        return min(phase_deg, 360.0 - phase_deg)
    return abs(phase_deg - 180.0)


def candidate_score(
    kind: Literal["solar", "lunar"],
    phase_deg: float,
    moon_lat_deg: float,
) -> tuple[float, float]:
    """
    Lower is better.

    Primary criterion:
    - closeness to exact phase target

    Secondary criterion:
    - closeness of Moon latitude to 0
    """
    return (
        phase_distance_for_kind(kind, phase_deg),
        abs(moon_lat_deg),
    )


def find_coarse_candidates(
    backend,
    start_utc: datetime,
    end_utc: datetime,
    step_hours: int = 6,
    phase_orb_deg: float = 15.0,
    node_lat_limit_deg: float = 1.0,
) -> list[EclipseCandidate]:
    """
    Scan a UTC datetime range and return coarse eclipse candidates.

    Logic:
    - solar candidate: near new moon and Moon latitude small
    - lunar candidate: near full moon and Moon latitude small

    This is intentionally coarse. Later we refine the candidate time.
    """
    if start_utc.tzinfo is None or end_utc.tzinfo is None:
        raise ValueError("start_utc and end_utc must be timezone-aware")

    start_utc = start_utc.astimezone(timezone.utc)
    end_utc = end_utc.astimezone(timezone.utc)

    if end_utc < start_utc:
        raise ValueError("end_utc must be >= start_utc")

    results: list[EclipseCandidate] = []
    dt = start_utc
    step = timedelta(hours=step_hours)

    while dt <= end_utc:
        sun_lon, moon_lon, moon_lat = backend.get_ecliptic_coords(dt)
        phase = phase_angle_deg(sun_lon, moon_lon)

        if abs(moon_lat) <= node_lat_limit_deg:
            if is_near_new_moon(phase, orb_deg=phase_orb_deg):
                results.append(
                    EclipseCandidate(
                        kind="solar",
                        time_utc=dt,
                        phase_deg=phase,
                        moon_lat_deg=moon_lat,
                        sun_lon_deg=sun_lon,
                        moon_lon_deg=moon_lon,
                    )
                )
            elif is_near_full_moon(phase, orb_deg=phase_orb_deg):
                results.append(
                    EclipseCandidate(
                        kind="lunar",
                        time_utc=dt,
                        phase_deg=phase,
                        moon_lat_deg=moon_lat,
                        sun_lon_deg=sun_lon,
                        moon_lon_deg=moon_lon,
                    )
                )

        dt += step

    return results


def _is_better_candidate(a: EclipseCandidate, b: EclipseCandidate) -> bool:
    """
    Return True if candidate a is better than candidate b.
    """
    return candidate_score(a.kind, a.phase_deg, a.moon_lat_deg) < candidate_score(
        b.kind, b.phase_deg, b.moon_lat_deg
    )


def merge_coarse_candidates(
    candidates: list[EclipseCandidate],
    cluster_hours: int = 36,
) -> list[EclipseCandidate]:
    """
    Merge nearby coarse hits into a single representative candidate.

    Rules:
    - candidates must be same kind (solar/lunar)
    - if times are within cluster_hours, they belong to same cluster
    - keep the best candidate in each cluster
    """
    if not candidates:
        return []

    sorted_candidates = sorted(candidates, key=lambda c: (c.kind, c.time_utc))

    merged: list[EclipseCandidate] = []
    current_best = sorted_candidates[0]
    current_cluster_end = current_best.time_utc + timedelta(hours=cluster_hours)

    for c in sorted_candidates[1:]:
        same_kind = c.kind == current_best.kind
        close_in_time = c.time_utc <= current_cluster_end

        if same_kind and close_in_time:
            if _is_better_candidate(c, current_best):
                current_best = c
            current_cluster_end = max(
                current_cluster_end,
                c.time_utc + timedelta(hours=cluster_hours),
            )
        else:
            merged.append(current_best)
            current_best = c
            current_cluster_end = c.time_utc + timedelta(hours=cluster_hours)

    merged.append(current_best)
    return merged


def _candidate_at_time(
    backend,
    kind: Literal["solar", "lunar"],
    dt: datetime,
) -> EclipseCandidate:
    sun_lon, moon_lon, moon_lat = backend.get_ecliptic_coords(dt)
    phase = phase_angle_deg(sun_lon, moon_lon)
    return EclipseCandidate(
        kind=kind,
        time_utc=dt,
        phase_deg=phase,
        moon_lat_deg=moon_lat,
        sun_lon_deg=sun_lon,
        moon_lon_deg=moon_lon,
    )


def _refine_once(
    backend,
    candidate: EclipseCandidate,
    window_hours: int,
    step_minutes: int,
) -> EclipseCandidate:
    """
    Search around candidate.time_utc and return the best sampled time.
    """
    half_window = timedelta(hours=window_hours)
    step = timedelta(minutes=step_minutes)

    start_utc = candidate.time_utc - half_window
    end_utc = candidate.time_utc + half_window

    best = _candidate_at_time(backend, candidate.kind, start_utc)
    dt = start_utc

    while dt <= end_utc:
        current = _candidate_at_time(backend, candidate.kind, dt)
        if _is_better_candidate(current, best):
            best = current
        dt += step

    return best


def refine_candidate_time(
    backend,
    candidate: EclipseCandidate,
) -> EclipseCandidate:
    """
    Refine a coarse candidate in three passes:

    1. ±12h, step 60m
    2. ±3h,  step 10m
    3. ±1h,  step 1m
    """
    best = candidate
    best = _refine_once(backend, best, window_hours=12, step_minutes=60)
    best = _refine_once(backend, best, window_hours=3, step_minutes=10)
    best = _refine_once(backend, best, window_hours=1, step_minutes=1)
    return best


def refine_candidates(
    backend,
    candidates: list[EclipseCandidate],
) -> list[EclipseCandidate]:
    """
    Refine each merged candidate independently.
    """
    return [refine_candidate_time(backend, c) for c in candidates]


def final_eclipse_filter(
    candidates: list[EclipseCandidate],
    max_phase_dist_deg: float = 1.0,
    max_abs_moon_lat_deg: float = 1.0,
) -> list[EclipseCandidate]:
    """
    Final strict screening after refinement.

    Keep only candidates that are:
    - close enough to exact syzygy
    - close enough to the node
    """
    filtered: list[EclipseCandidate] = []

    for c in candidates:
        phase_dist = phase_distance_for_kind(c.kind, c.phase_deg)
        if phase_dist <= max_phase_dist_deg and abs(c.moon_lat_deg) <= max_abs_moon_lat_deg:
            filtered.append(c)

    return filtered


def find_eclipses_for_year(
    backend,
    year: int,
    step_hours: int = 6,
    phase_orb_deg: float = 15.0,
    node_lat_limit_deg: float = 1.0,
    cluster_hours: int = 36,
    max_phase_dist_deg: float = 1.0,
    max_abs_moon_lat_deg: float = 1.0,
) -> list[EclipseCandidate]:
    """
    Find final eclipse candidates for a single UTC year.
    """
    start_utc = datetime(year, 1, 1, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(year, 12, 31, 23, 59, tzinfo=timezone.utc)

    coarse_candidates = find_coarse_candidates(
        backend=backend,
        start_utc=start_utc,
        end_utc=end_utc,
        step_hours=step_hours,
        phase_orb_deg=phase_orb_deg,
        node_lat_limit_deg=node_lat_limit_deg,
    )

    merged_candidates = merge_coarse_candidates(
        coarse_candidates,
        cluster_hours=cluster_hours,
    )

    refined_candidates = refine_candidates(
        backend,
        merged_candidates,
    )

    final_candidates = final_eclipse_filter(
        refined_candidates,
        max_phase_dist_deg=max_phase_dist_deg,
        max_abs_moon_lat_deg=max_abs_moon_lat_deg,
    )

    return sorted(final_candidates, key=lambda c: c.time_utc)