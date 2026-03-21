"""
Weekday / Vara constants.

id:
1 = Sunday
...
7 = Saturday
"""

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
    if 1 <= weekday_id <= 7:
        return WEEKDAYS[weekday_id - 1][lang]
    raise ValueError("Weekday id must be between 1 and 7")


if __name__ == "__main__":
    print("Weekday List")
    print("----------------")
    for w in WEEKDAYS:
        print(f"{w['id']:2d}: {w['en']:<10} ({w['np']})")