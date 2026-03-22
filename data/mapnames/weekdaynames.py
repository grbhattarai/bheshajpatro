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
    if 1 <= weekday_id <= 7:
        return WEEKDAYS[weekday_id - 1][lang]
    raise ValueError("Weekday id must be between 1 and 7")


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
    if not 0 <= int(py_weekday) <= 6:
        raise ValueError("Python weekday must be between 0 and 6")
    return ((int(py_weekday) + 1) % 7) + 1


def ketaki_weekday_to_display_id(ketaki_weekday: int) -> int:
    """
    Convert Ketaki / Ahargana weekday numbering to shared display id.

    Assumed Ketaki convention:
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

    Adjust this mapping if your final Ketaki convention differs.
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
    return mapping[int(ketaki_weekday) % 7]


def weekday_name_from_python(py_weekday: int, lang: str = "en") -> str:
    """
    Convenience helper for Python civil-date weekday.
    """
    return get_weekday_name(python_weekday_to_display_id(py_weekday), lang)


def weekday_name_from_ketaki(ketaki_weekday: int, lang: str = "en") -> str:
    """
    Convenience helper for Ketaki / Ahargana weekday.
    """
    return get_weekday_name(ketaki_weekday_to_display_id(ketaki_weekday), lang)


if __name__ == "__main__":
    print("Weekday List")
    print("----------------")
    for w in WEEKDAYS:
        print(f"{w['id']:2d}: {w['en']:<10} ({w['np']})")

    print("\nPython weekday mapping")
    for i in range(7):
        print(i, "->", python_weekday_to_display_id(i), "->", weekday_name_from_python(i))

    print("\nKetaki weekday mapping")
    for i in range(7):
        print(i, "->", ketaki_weekday_to_display_id(i), "->", weekday_name_from_ketaki(i))