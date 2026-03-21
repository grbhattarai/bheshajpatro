"""
English / Gregorian month constants.
"""

EMONTH = [
    {"id": 1, "en": "January", "np": "जनवरी"},
    {"id": 2, "en": "February", "np": "फेब्रुअरी"},
    {"id": 3, "en": "March", "np": "मार्च"},
    {"id": 4, "en": "April", "np": "अप्रिल"},
    {"id": 5, "en": "May", "np": "मे"},
    {"id": 6, "en": "June", "np": "जुन"},
    {"id": 7, "en": "July", "np": "जुलाई"},
    {"id": 8, "en": "August", "np": "अगस्ट"},
    {"id": 9, "en": "September", "np": "सेप्टेम्बर"},
    {"id": 10, "en": "October", "np": "अक्टोबर"},
    {"id": 11, "en": "November", "np": "नोभेम्बर"},
    {"id": 12, "en": "December", "np": "डिसेम्बर"},
]


def get_emonth_name(month_id: int, lang: str = "en") -> str:
    if 1 <= month_id <= 12:
        return EMONTH[month_id - 1][lang]
    raise ValueError("Month id must be between 1 and 12")


if __name__ == "__main__":
    print("English Month List")
    print("----------------")
    for m in EMONTH:
        print(f"{m['id']:2d}: {m['en']:<12} ({m['np']})")