"""
Ritu constants.
"""

RITU = [
    {"id": 1, "en": "Vasanta", "np": "वसन्त"},
    {"id": 2, "en": "Grishma", "np": "ग्रीष्म"},
    {"id": 3, "en": "Varsha", "np": "वर्षा"},
    {"id": 4, "en": "Sharad", "np": "शरद्"},
    {"id": 5, "en": "Hemanta", "np": "हेमन्त"},
    {"id": 6, "en": "Shishira", "np": "शिशिर"},
]


def get_ritu_name(ritu_id: int, lang: str = "en") -> str:
    if 1 <= ritu_id <= 6:
        return RITU[ritu_id - 1][lang]
    raise ValueError("Ritu id must be between 1 and 6")


if __name__ == "__main__":
    print("Ritu List")
    print("----------------")
    for r in RITU:
        print(f"{r['id']:2d}: {r['en']:<10} ({r['np']})")