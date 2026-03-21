"""
Rashi constants.

id:
1 = Mesha
...
12 = Mina
"""

RASHI = [
    {"id": 1, "en": "Mesha", "np": "मेष"},
    {"id": 2, "en": "Vrishabha", "np": "वृषभ"},
    {"id": 3, "en": "Mithuna", "np": "मिथुन"},
    {"id": 4, "en": "Karka", "np": "कर्कट"},
    {"id": 5, "en": "Simha", "np": "सिंह"},
    {"id": 6, "en": "Kanya", "np": "कन्या"},
    {"id": 7, "en": "Tula", "np": "तुला"},
    {"id": 8, "en": "Vrischika", "np": "वृश्चिक"},
    {"id": 9, "en": "Dhanu", "np": "धनु"},
    {"id": 10, "en": "Makara", "np": "मकर"},
    {"id": 11, "en": "Kumbha", "np": "कुम्भ"},
    {"id": 12, "en": "Mina", "np": "मीन"},
]


def get_rashi_name(rashi_id: int, lang: str = "en") -> str:
    if 1 <= rashi_id <= 12:
        return RASHI[rashi_id - 1][lang]
    raise ValueError("Rashi id must be between 1 and 12")


if __name__ == "__main__":
    print("Rashi List")
    print("----------------")
    for r in RASHI:
        print(f"{r['id']:2d}: {r['en']:<10} ({r['np']})")