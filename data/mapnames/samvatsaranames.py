"""
60 Samvatsara names.

Each samvatsara contains:
- id : 1–60
- en : English / transliterated name
- np : Nepali / Devanagari name
"""

SAMVATSARA = [
    {"id": 1, "en": "Prabhava", "np": "प्रभव"},
    {"id": 2, "en": "Vibhava", "np": "विभव"},
    {"id": 3, "en": "Shukla", "np": "शुक्ल"},
    {"id": 4, "en": "Pramoda", "np": "प्रमोद"},
    {"id": 5, "en": "Prajapati", "np": "प्रजापति"},
    {"id": 6, "en": "Angira", "np": "अङ्गिरा"},
    {"id": 7, "en": "Shrimukha", "np": "श्रीमुख"},
    {"id": 8, "en": "Bhava", "np": "भाव"},
    {"id": 9, "en": "Yuva", "np": "युवा"},
    {"id": 10, "en": "Dhata", "np": "धाता"},
    {"id": 11, "en": "Ishwara", "np": "ईश्वर"},
    {"id": 12, "en": "Bahudhanya", "np": "बहुधान्य"},
    {"id": 13, "en": "Pramathi", "np": "प्रमाथी"},
    {"id": 14, "en": "Vikrama", "np": "विक्रम"},
    {"id": 15, "en": "Vrisha", "np": "वृष"},
    {"id": 16, "en": "Chitrabhanu", "np": "चित्रभानु"},
    {"id": 17, "en": "Svabhanu", "np": "स्वभानु"},
    {"id": 18, "en": "Tarana", "np": "तारण"},
    {"id": 19, "en": "Parthiva", "np": "पार्थिव"},
    {"id": 20, "en": "Vyaya", "np": "व्यय"},
    {"id": 21, "en": "Sarvajit", "np": "सर्वजित्"},
    {"id": 22, "en": "Sarvadhari", "np": "सर्वधारी"},
    {"id": 23, "en": "Virodhi", "np": "विरोधी"},
    {"id": 24, "en": "Vikrti", "np": "विकृति"},
    {"id": 25, "en": "Khara", "np": "खर"},
    {"id": 26, "en": "Nandana", "np": "नन्दन"},
    {"id": 27, "en": "Vijaya", "np": "विजय"},
    {"id": 28, "en": "Jaya", "np": "जय"},
    {"id": 29, "en": "Manmatha", "np": "मन्मथ"},
    {"id": 30, "en": "Durmukha", "np": "दुर्मुख"},
    {"id": 31, "en": "Hevilambi", "np": "हेविलम्बी"},
    {"id": 32, "en": "Vilambi", "np": "विलम्बी"},
    {"id": 33, "en": "Vikari", "np": "विकारी"},
    {"id": 34, "en": "Sharvari", "np": "शार्वरी"},
    {"id": 35, "en": "Plava", "np": "प्लव"},
    {"id": 36, "en": "Shubhakrit", "np": "शुभकृत्"},
    {"id": 37, "en": "Shobhakrit", "np": "शोभकृत्"},
    {"id": 38, "en": "Krodhi", "np": "क्रोधी"},
    {"id": 39, "en": "Vishvavasu", "np": "विश्वावसु"},
    {"id": 40, "en": "Parabhava", "np": "पराभव"},
    {"id": 41, "en": "Plavanga", "np": "प्लवङ्ग"},
    {"id": 42, "en": "Kilaka", "np": "कीलक"},
    {"id": 43, "en": "Saumya", "np": "सौम्य"},
    {"id": 44, "en": "Sadharana", "np": "साधारण"},
    {"id": 45, "en": "Virodhikrit", "np": "विरोधिकृत्"},
    {"id": 46, "en": "Paridhavi", "np": "परिधावी"},
    {"id": 47, "en": "Pramadi", "np": "प्रमादी"},
    {"id": 48, "en": "Ananda", "np": "आनन्द"},
    {"id": 49, "en": "Rakshasa", "np": "राक्षस"},
    {"id": 50, "en": "Nala", "np": "नल"},
    {"id": 51, "en": "Pingala", "np": "पिङ्गल"},
    {"id": 52, "en": "Kalayukta", "np": "कालयुक्त"},
    {"id": 53, "en": "Siddharthi", "np": "सिद्धार्थी"},
    {"id": 54, "en": "Raudra", "np": "रौद्र"},
    {"id": 55, "en": "Durmati", "np": "दुर्मति"},
    {"id": 56, "en": "Dundubhi", "np": "दुन्दुभि"},
    {"id": 57, "en": "Rudhirodgari", "np": "रुधिरोद्गारी"},
    {"id": 58, "en": "Raktakshi", "np": "रक्ताक्षी"},
    {"id": 59, "en": "Krodhana", "np": "क्रोधन"},
    {"id": 60, "en": "Akshaya", "np": "अक्षय"},
]


def get_samvatsara_name(samvatsara_id: int, lang: str = "en") -> str:
    if 1 <= samvatsara_id <= 60:
        return SAMVATSARA[samvatsara_id - 1][lang]
    raise ValueError("Samvatsara id must be between 1 and 60")


if __name__ == "__main__":
    print("Samvatsara List")
    print("----------------")
    for s in SAMVATSARA:
        print(f"{s['id']:2d}: {s['en']:<14} ({s['np']})")