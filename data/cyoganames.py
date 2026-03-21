"""
Anandadi (28) Yoga constants.

Each entry:
- id : 1–28
- en : English / transliterated name
- np : Nepali / Devanagari name
"""

CYOGA = [
    {"id": 1, "en": "Ananda", "np": "आनन्द"},
    {"id": 2, "en": "Kaladanda", "np": "कालदण्ड"},
    {"id": 3, "en": "Dhumra", "np": "धूम्र"},
    {"id": 4, "en": "Dhata", "np": "धाता"},
    {"id": 5, "en": "Saumya", "np": "सौम्य"},
    {"id": 6, "en": "Dhvaja", "np": "ध्वज"},
    {"id": 7, "en": "Shrivatsa", "np": "श्रीवत्स"},
    {"id": 8, "en": "Vajra", "np": "वज्र"},
    {"id": 9, "en": "Mudgara", "np": "मुद्गर"},
    {"id": 10, "en": "Chhatra", "np": "छत्र"},
    {"id": 11, "en": "Mitra", "np": "मित्र"},
    {"id": 12, "en": "Manasa", "np": "मानस"},
    {"id": 13, "en": "Padma", "np": "पद्म"},
    {"id": 14, "en": "Lamba", "np": "लम्ब"},
    {"id": 15, "en": "Utpata", "np": "उत्पात"},
    {"id": 16, "en": "Mrityu", "np": "मृत्यु"},
    {"id": 17, "en": "Kana", "np": "काण"},
    {"id": 18, "en": "Siddha", "np": "सिद्ध"},
    {"id": 19, "en": "Subha", "np": "शुभ"},
    {"id": 20, "en": "Amrita", "np": "अमृत"},
    {"id": 21, "en": "Musala", "np": "मुसल"},
    {"id": 22, "en": "Gada", "np": "गदा"},
    {"id": 23, "en": "Matanga", "np": "मतंग"},
    {"id": 24, "en": "Rakshasa", "np": "राक्षस"},
    {"id": 25, "en": "Chara", "np": "चर"},
    {"id": 26, "en": "Sthira", "np": "स्थिर"},
    {"id": 27, "en": "Vardhamana", "np": "वर्धमान"},
    {"id": 28, "en": "Dhruva", "np": "ध्रुव"},
]


def get_cyoga_name(yoga_id: int, lang: str = "en") -> str:
    if 1 <= yoga_id <= 28:
        return CYOGA[yoga_id - 1][lang]
    raise ValueError("Yoga combo id must be between 1 and 28")


if __name__ == "__main__":
    print("Anandadi Yoga List")
    print("--------------------")
    for y in CYOGA:
        print(f"{y['id']:2d}: {y['en']:<12} ({y['np']})")