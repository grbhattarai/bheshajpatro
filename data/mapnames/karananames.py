"""
Karana constants.

There are 11 named karanas.
In actual use, karana occurrence in tithis follows a repeating pattern,
but the names themselves are listed here.
"""

KARANA = [
    {"id": 1, "en": "Bava", "np": "बव"},
    {"id": 2, "en": "Balava", "np": "बालव"},
    {"id": 3, "en": "Kaulava", "np": "कौलव"},
    {"id": 4, "en": "Taitila", "np": "तैतिल"},
    {"id": 5, "en": "Gara", "np": "गर"},
    {"id": 6, "en": "Vanija", "np": "वणिज"},
    {"id": 7, "en": "Vishti", "np": "विष्टि"},
    {"id": 8, "en": "Shakuni", "np": "शकुनि"},
    {"id": 9, "en": "Chatushpada", "np": "चतुष्पद"},
    {"id": 10, "en": "Naga", "np": "नाग"},
    {"id": 11, "en": "Kimstughna", "np": "किंस्तुघ्न"},
]


def get_karana_name(karana_id: int, lang: str = "en") -> str:
    if 1 <= karana_id <= 11:
        return KARANA[karana_id - 1][lang]
    raise ValueError("Karana id must be between 1 and 11")


if __name__ == "__main__":
    print("Karana List")
    print("----------------")
    for k in KARANA:
        print(f"{k['id']:2d}: {k['en']:<12} ({k['np']})")