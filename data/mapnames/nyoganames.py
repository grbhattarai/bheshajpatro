"""
Yoga constants.

Each yoga contains:
- id : 1–27
- en : English name
- np : Nepali / Devanagari name
"""

NYOGA = [
    {"id": 1, "en": "Vishkambha", "np": "विष्कम्भ"},
    {"id": 2, "en": "Priti", "np": "प्रीति"},
    {"id": 3, "en": "Ayushman", "np": "आयुष्मान"},
    {"id": 4, "en": "Saubhagya", "np": "सौभाग्य"},
    {"id": 5, "en": "Shobhana", "np": "शोभन"},
    {"id": 6, "en": "Atiganda", "np": "अतिगण्ड"},
    {"id": 7, "en": "Sukarma", "np": "सुकर्म"},
    {"id": 8, "en": "Dhriti", "np": "धृति"},
    {"id": 9, "en": "Shula", "np": "शूल"},
    {"id": 10, "en": "Ganda", "np": "गण्ड"},
    {"id": 11, "en": "Vriddhi", "np": "वृद्धि"},
    {"id": 12, "en": "Dhruva", "np": "ध्रुव"},
    {"id": 13, "en": "Vyaghata", "np": "व्याघात"},
    {"id": 14, "en": "Harshana", "np": "हर्षण"},
    {"id": 15, "en": "Vajra", "np": "वज्र"},
    {"id": 16, "en": "Siddhi", "np": "सिद्धि"},
    {"id": 17, "en": "Vyatipata", "np": "व्यतीपात"},
    {"id": 18, "en": "Variyana", "np": "वरीयान"},
    {"id": 19, "en": "Parigha", "np": "परिघ"},
    {"id": 20, "en": "Shiva", "np": "शिव"},
    {"id": 21, "en": "Siddha", "np": "सिद्ध"},
    {"id": 22, "en": "Sadhya", "np": "साध्य"},
    {"id": 23, "en": "Shubha", "np": "शुभ"},
    {"id": 24, "en": "Shukla", "np": "शुक्ल"},
    {"id": 25, "en": "Brahma", "np": "ब्रह्म"},
    {"id": 26, "en": "Indra", "np": "इन्द्र"},
    {"id": 27, "en": "Vaidhriti", "np": "वैधृति"},
]


def get_nyoga_name(yoga_id: int, lang: str = "en") -> str:
    if 1 <= yoga_id <= 27:
        return NYOGA[yoga_id - 1][lang]
    raise ValueError("Yoga id must be between 1 and 27")


if __name__ == "__main__":
    print("Yoga List")
    print("----------------")
    for y in NYOGA:
        print(f"{y['id']:2d}: {y['en']:<12} ({y['np']})")