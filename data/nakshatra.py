"""
Nakshatra constants.

Each nakshatra contains:
- id : 1–27
- en : English name
- np : Nepali / Devanagari name
"""

NAKSHATRA = [
    {"id": 1, "en": "Ashwini", "np": "अश्विनी"},
    {"id": 2, "en": "Bharani", "np": "भरणी"},
    {"id": 3, "en": "Krittika", "np": "कृत्तिका"},
    {"id": 4, "en": "Rohini", "np": "रोहिणी"},
    {"id": 5, "en": "Mrigashira", "np": "मृगशीर्ष"},
    {"id": 6, "en": "Ardra", "np": "आर्द्रा"},
    {"id": 7, "en": "Punarvasu", "np": "पुनर्वसु"},
    {"id": 8, "en": "Pushya", "np": "पुष्य"},
    {"id": 9, "en": "Ashlesha", "np": "आश्लेषा"},
    {"id": 10, "en": "Magha", "np": "मघा"},
    {"id": 11, "en": "Purva Phalguni", "np": "पूर्व फाल्गुनी"},
    {"id": 12, "en": "Uttara Phalguni", "np": "उत्तर फाल्गुनी"},
    {"id": 13, "en": "Hasta", "np": "हस्त"},
    {"id": 14, "en": "Chitra", "np": "चित्रा"},
    {"id": 15, "en": "Swati", "np": "स्वाती"},
    {"id": 16, "en": "Vishakha", "np": "विशाखा"},
    {"id": 17, "en": "Anuradha", "np": "अनुराधा"},
    {"id": 18, "en": "Jyeshtha", "np": "ज्येष्ठा"},
    {"id": 19, "en": "Mula", "np": "मूला"},
    {"id": 20, "en": "Purva Ashadha", "np": "पूर्वाषाढा"},
    {"id": 21, "en": "Uttara Ashadha", "np": "उत्तराषाढा"},
    {"id": 22, "en": "Shravana", "np": "श्रवण"},
    {"id": 23, "en": "Dhanishta", "np": "धनिष्ठा"},
    {"id": 24, "en": "Shatabhisha", "np": "शतभिषा"},
    {"id": 25, "en": "Purva Bhadrapada", "np": "पूर्व भाद्रपदा"},
    {"id": 26, "en": "Uttara Bhadrapada", "np": "उत्तर भाद्रपदा"},
    {"id": 27, "en": "Revati", "np": "रेवती"},
]


def get_nakshatra_name(nakshatra_id: int, lang: str = "en") -> str:
    """
    Return nakshatra name in requested language.

    lang options:
        "en" -> English
        "np" -> Nepali / Devanagari
    """
    if 1 <= nakshatra_id <= 27:
        return NAKSHATRA[nakshatra_id - 1][lang]
    raise ValueError("Nakshatra id must be between 1 and 27")


# Sanity check in Terminal

if __name__ == "__main__":
    print("Nakshatra List")
    print("----------------")

    for n in NAKSHATRA:
        print(f"{n['id']:2d}: {n['en']}  ({n['np']})")