"""
Tithi constants.

Each tithi contains:
- id : 1–30
- en : English name
- np : Nepali / Devanagari name
"""

TITHI = [
    {"id": 1, "en": "Shukla Pratipada", "np": "शुक्ल प्रतिपदा"},
    {"id": 2, "en": "Shukla Dwitiya", "np": "शुक्ल द्वितीया"},
    {"id": 3, "en": "Shukla Tritiya", "np": "शुक्ल तृतीया"},
    {"id": 4, "en": "Shukla Chaturthi", "np": "शुक्ल चतुर्थी"},
    {"id": 5, "en": "Shukla Panchami", "np": "शुक्ल पञ्चमी"},
    {"id": 6, "en": "Shukla Shashthi", "np": "शुक्ल षष्ठी"},
    {"id": 7, "en": "Shukla Saptami", "np": "शुक्ल सप्तमी"},
    {"id": 8, "en": "Shukla Ashtami", "np": "शुक्ल अष्टमी"},
    {"id": 9, "en": "Shukla Navami", "np": "शुक्ल नवमी"},
    {"id": 10, "en": "Shukla Dashami", "np": "शुक्ल दशमी"},
    {"id": 11, "en": "Shukla Ekadashi", "np": "शुक्ल एकादशी"},
    {"id": 12, "en": "Shukla Dwadashi", "np": "शुक्ल द्वादशी"},
    {"id": 13, "en": "Shukla Trayodashi", "np": "शुक्ल त्रयोदशी"},
    {"id": 14, "en": "Shukla Chaturdashi", "np": "शुक्ल चतुर्दशी"},
    {"id": 15, "en": "Purnima", "np": "पूर्णिमा"},
    {"id": 16, "en": "Krishna Pratipada", "np": "कृष्ण प्रतिपदा"},
    {"id": 17, "en": "Krishna Dwitiya", "np": "कृष्ण द्वितीया"},
    {"id": 18, "en": "Krishna Tritiya", "np": "कृष्ण तृतीया"},
    {"id": 19, "en": "Krishna Chaturthi", "np": "कृष्ण चतुर्थी"},
    {"id": 20, "en": "Krishna Panchami", "np": "कृष्ण पञ्चमी"},
    {"id": 21, "en": "Krishna Shashthi", "np": "कृष्ण षष्ठी"},
    {"id": 22, "en": "Krishna Saptami", "np": "कृष्ण सप्तमी"},
    {"id": 23, "en": "Krishna Ashtami", "np": "कृष्ण अष्टमी"},
    {"id": 24, "en": "Krishna Navami", "np": "कृष्ण नवमी"},
    {"id": 25, "en": "Krishna Dashami", "np": "कृष्ण दशमी"},
    {"id": 26, "en": "Krishna Ekadashi", "np": "कृष्ण एकादशी"},
    {"id": 27, "en": "Krishna Dwadashi", "np": "कृष्ण द्वादशी"},
    {"id": 28, "en": "Krishna Trayodashi", "np": "कृष्ण त्रयोदशी"},
    {"id": 29, "en": "Krishna Chaturdashi", "np": "कृष्ण चतुर्दशी"},
    {"id": 30, "en": "Amavasya", "np": "अमावस्या"},
]


def get_tithi_name(tithi_id: int, lang: str = "en") -> str:
    if 1 <= tithi_id <= 30:
        return TITHI[tithi_id - 1][lang]
    raise ValueError("Tithi id must be between 1 and 30")


if __name__ == "__main__":
    print("Tithi List")
    print("----------------")
    for t in TITHI:
        print(f"{t['id']:2d}: {t['en']:<24} ({t['np']})")