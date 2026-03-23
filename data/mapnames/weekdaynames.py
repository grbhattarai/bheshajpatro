"""
Weekday / Vara display constants and normalization helpers.

Shared display convention used by UI and final Panchanga output:

    1 = Sunday
    2 = Monday
    3 = Tuesday
    4 = Wednesday
    5 = Thursday
    6 = Friday
    7 = Saturday

Important:
- Engines may use different internal weekday numbering systems.
- Convert engine-native weekday values into this shared display id
  before asking for the weekday name.
"""

from __future__ import annotations

WEEKDAYS = [
    {"id": 1, "en": "Sunday", "np": "आइतबार"},
    {"id": 2, "en": "Monday", "np": "सोमबार"},
    {"id": 3, "en": "Tuesday", "np": "मङ्गलबार"},
    {"id": 4, "en": "Wednesday", "np": "बुधबार"},
    {"id": 5, "en": "Thursday", "np": "बिहीबार"},
    {"id": 6, "en": "Friday", "np": "शुक्रबार"},
    {"id": 7, "en": "Saturday", "np": "शनिबार"},
]


def get_weekday_name(weekday_id: int, lang: str = "en") -> str:
    """
    Return weekday name from shared display weekday id.

    Shared convention:
        1 = Sunday
        ...
        7 = Saturday
    """
    wid = int(weekday_id)
    if not 1 <= wid <= 7:
        raise ValueError("Weekday id must be between 1 and 7")

    if lang not in ("en", "np"):
        raise ValueError("Language must be 'en' or 'np'")

    return WEEKDAYS[wid - 1][lang]


def normalize_weekday_id(weekday_id: int) -> int:
    """
    Normalize any integer into shared display weekday id range 1..7.
    """
    return ((int(weekday_id) - 1) % 7) + 1


def python_weekday_to_display_id(py_weekday: int) -> int:
    """
    Convert Python weekday() numbering to shared display id.

    Python:
        0 = Monday
        1 = Tuesday
        2 = Wednesday
        3 = Thursday
        4 = Friday
        5 = Saturday
        6 = Sunday

    Shared display:
        1 = Sunday
        2 = Monday
        3 = Tuesday
        4 = Wednesday
        5 = Thursday
        6 = Friday
        7 = Saturday
    """
    pw = int(py_weekday)
    if not 0 <= pw <= 6:
        raise ValueError("Python weekday must be between 0 and 6")

    return ((pw + 1) % 7) + 1


def julian_weekday_to_display_id(julian_weekday: int) -> int:
    """
    Convert Julian/Ketaki weekday numbering to shared display id.

    Expected Julian/Ketaki convention:
        0 = Wednesday
        1 = Thursday
        2 = Friday
        3 = Saturday
        4 = Sunday
        5 = Monday
        6 = Tuesday

    Shared display:
        1 = Sunday
        2 = Monday
        3 = Tuesday
        4 = Wednesday
        5 = Thursday
        6 = Friday
        7 = Saturday

    Adjust this mapping if your final engine convention differs.
    """
    mapping = {
        0: 4,  # Wednesday
        1: 5,  # Thursday
        2: 6,  # Friday
        3: 7,  # Saturday
        4: 1,  # Sunday
        5: 2,  # Monday
        6: 3,  # Tuesday
    }
    return mapping[int(julian_weekday) % 7]


def ketaki_weekday_to_display_id(ketaki_weekday: int) -> int:
    """
    Backward-compatible alias for Ketaki/JD weekday conversion.
    """
    return julian_weekday_to_display_id(ketaki_weekday)


def weekday_name_from_python(py_weekday: int, lang: str = "en") -> str:
    """
    Convenience helper for Python civil-date weekday.
    """
    return get_weekday_name(python_weekday_to_display_id(py_weekday), lang)


def weekday_name_from_julian(julian_weekday: int, lang: str = "en") -> str:
    """
    Convenience helper for Julian/Ketaki weekday.
    """
    return get_weekday_name(julian_weekday_to_display_id(julian_weekday), lang)


def weekday_name_from_ketaki(ketaki_weekday: int, lang: str = "en") -> str:
    """
    Backward-compatible alias for Ketaki/JD weekday name.
    """
    return weekday_name_from_julian(ketaki_weekday, lang)