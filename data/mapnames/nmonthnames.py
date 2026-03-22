"""
Lunar month constants.
"""

NMONTH = [
    {"id": 1, "en": "Vaishakha", "np": "वैशाख"},
    {"id": 2, "en": "Jyeshtha", "np": "ज्येष्ठ"},
    {"id": 3, "en": "Ashadha", "np": "आषाढ"},
    {"id": 4, "en": "Shrawana", "np": "श्रावण"},
    {"id": 5, "en": "Bhadrapada", "np": "भाद्रपद"},
    {"id": 6, "en": "Ashwin", "np": "आश्विन"},
    {"id": 7, "en": "Kartik", "np": "कार्तिक"},
    {"id": 8, "en": "Mangsir", "np": "मार्गशीर्ष"},
    {"id": 9, "en": "Poush", "np": "पौष"},
    {"id": 10, "en": "Magha", "np": "माघ"},
    {"id": 11, "en": "Phalguna", "np": "फाल्गुण"},
    {"id": 12, "en": "Chaitra", "np": "चैत्र"},
]


def get_nmonth_name(masa_id: int, lang: str = "en") -> str:
    if 1 <= masa_id <= 12:
        return NMONTH[masa_id - 1][lang]
    raise ValueError("Masa id must be between 1 and 12")


if __name__ == "__main__":
    print("Masa List")
    print("----------------")
    for m in NMONTH:
        print(f"{m['id']:2d}: {m['en']:<12} ({m['np']})")