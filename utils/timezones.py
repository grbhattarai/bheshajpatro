# bheshajpatro/utils/timezones.py
from __future__ import annotations

from zoneinfo import ZoneInfo, available_timezones
from typing import Optional
from bheshajpatro.utils.exceptions import TimezoneError


def get_timezone(tz: str | None) -> Optional[ZoneInfo]:
    """
    Return ZoneInfo instance or raise TimezoneError.
    """
    if tz is None:
        return None

    try:
        return ZoneInfo(tz)
    except Exception:
        raise TimezoneError(f"Unknown or unsupported timezone: {tz}")


def is_valid_timezone(tz: str) -> bool:
    return tz in available_timezones()
