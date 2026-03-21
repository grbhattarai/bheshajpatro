"""
Graha constants.

Useful for charting, panchanga display, and future transit logic.
"""

GRAHA = [
    {"id": 1, "en": "Surya", "np": "सूर्य"},
    {"id": 2, "en": "Chandra", "np": "चन्द्र"},
    {"id": 3, "en": "Mangala", "np": "मङ्गल"},
    {"id": 4, "en": "Budha", "np": "बुध"},
    {"id": 5, "en": "Guru", "np": "गुरु"},
    {"id": 6, "en": "Shukra", "np": "शुक्र"},
    {"id": 7, "en": "Shani", "np": "शनि"},
    {"id": 8, "en": "Rahu", "np": "राहु"},
    {"id": 9, "en": "Ketu", "np": "केतु"},
]


def get_graha_name(graha_id: int, lang: str = "en") -> str:
    if 1 <= graha_id <= 9:
        return GRAHA[graha_id - 1][lang]
    raise ValueError("Graha id must be between 1 and 9")


if __name__ == "__main__":
    print("Graha List")
    print("----------------")
    for g in GRAHA:
        print(f"{g['id']:2d}: {g['en']:<10} ({g['np']})")