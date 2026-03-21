# Copyright (c) 2025 Gandhi Bhattarai
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Central mapping definitions for Panchanga calculations.
#
# This module contains:
# - Graha name mappings
# - Day, Tithi, Nakshatra, Yoga, Karana mappings
# - Rashi names and solar month names

from __future__ import annotations

__all__ = [
    "GRAHA_NAME_MAP_EN_TO_SA",
    "GRAHA_KEYS",
    "DAY_NAME_MAP",
    "TITHI_NAME_MAP",
    "NAKSHATRA_NAME_MAP",
    "YOGA_NAME_MAP",
    "KARANA_NAME_MAP",
    "RASHI_NAME_MAP",
    "SUN_MONTH_NAME_MAP",
]

# ---------------------------------------------------------------------------
# Graha name maps
# ---------------------------------------------------------------------------

GRAHA_NAME_MAP_EN_TO_SA = {
    "sun": "surya",
    "moon": "chandra",
    "mars": "mangal",
    "mercury": "budha",
    "jupiter": "guru",
    "venus": "shukra",
    "saturn": "shani",
    "rahu": "rahu",
    "ketu": "ketu",
}

GRAHA_KEYS = [
    "surya",
    "chandra",
    "mangal",
    "budha",
    "guru",
    "shukra",
    "shani",
    "rahu",
    "ketu",
]

# ---------------------------------------------------------------------------
# Panchanga Name Maps
# ---------------------------------------------------------------------------

DAY_NAME_MAP = {
    0: "Wednesday",
    1: "Thursday",
    2: "Friday",
    3: "Saturday",
    4: "Sunday",
    5: "Monday",
    6: "Tuesday",
    7: "Wednesday",
}

TITHI_NAME_MAP = {
    0: "Amavasya",
    1: "Pratipada",
    2: "Dwitiya",
    3: "Tritiya",
    4: "Chaturthi",
    5: "Panchami",
    6: "Shashti",
    7: "Saptami",
    8: "Ashtami",
    9: "Navami",
    10: "Dashami",
    11: "Ekadashi",
    12: "Dwadashi",
    13: "Trayodashi",
    14: "Chaturdashi",
    15: "Purnima",
    16: "Pratipada",
    17: "Dwitiya",
    18: "Tritiya",
    19: "Chaturthi",
    20: "Panchami",
    21: "Shashti",
    22: "Saptami",
    23: "Ashtami",
    24: "Navami",
    25: "Dashami",
    26: "Ekadashi",
    27: "Dwadashi",
    28: "Trayodashi",
    29: "Chaturdashi",
    30: "Amavasya",
}

NAKSHATRA_NAME_MAP = {
    1: "Ashwini",
    2: "Bharani",
    3: "Kritika",
    4: "Rohini",
    5: "Mrigashira",
    6: "Ardra",
    7: "Punarvasu",
    8: "Pushya",
    9: "Ashlesha",
    10: "Magha",
    11: "P.Phalguni",
    12: "U.Phalguni",
    13: "Hasta",
    14: "Chitra",
    15: "Swati",
    16: "Vishakha",
    17: "Anuradha",
    18: "Jyeshta",
    19: "Moola",
    20: "Purvashadha",
    21: "Uttarashadha",
    22: "Shravan",
    23: "Dhanishta",
    24: "Shatabhisha",
    25: "P.Bhadrapada",
    26: "U.Bhadrapada",
    27: "Revati",
}

YOGA_NAME_MAP = {
    1: "Vishkumbha",
    2: "Priti",
    3: "Ayushman",
    4: "Saubhagya",
    5: "Shobhana",
    6: "Atiganda",
    7: "Sukarma",
    8: "Dhriti",
    9: "Shula",
    10: "Ganda",
    11: "Vriddhi",
    12: "Dhruva",
    13: "Vyaghata",
    14: "Harshana",
    15: "Vajra",
    16: "Siddhi",
    17: "Vyatipata",
    18: "Variyan",
    19: "Parigha",
    20: "Shiva",
    21: "Siddha",
    22: "Sadhya",
    23: "Shubha",
    24: "Shukla",
    25: "Brahma",
    26: "Indra",
    27: "Vaidhriti",
}

# Karana names (1..11)
KARANA_NAME_MAP = {
    1: "Bava",
    2: "Balava",
    3: "Kaulava",
    4: "Taitila",
    5: "Gara",
    6: "Vanija",
    7: "Vishti",        # also called Bhadra
    8: "Shakuni",
    9: "Chatuspad",
    10: "Nagava",
    11: "Kimstughna",
}

# ---------------------------------------------------------------------------
# Rashi / Month Maps
# ---------------------------------------------------------------------------

RASHI_NAME_MAP = {
    1: "Mesha",
    2: "Vrishav",
    3: "Mithuna",
    4: "Karkata",
    5: "Simha",
    6: "Kanya",
    7: "Tula",
    8: "Brischik",
    9: "Dhanau",
    10: "Makara",
    11: "Kumbha",
    12: "Meena",
}

SUN_MONTH_NAME_MAP = {
    1: "Baishakh",
    2: "Jeshtha",
    3: "Ashadha",
    4: "Shravan",
    5: "Bhadra",
    6: "Ashwin",
    7: "Kartik",
    8: "Mansir",
    9: "Pausha",
    10: "Magha",
    11: "Phalgun",
    12: "Chaitra",
}
