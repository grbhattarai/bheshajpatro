# bheshajpatro/utils/paths.py

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------
# Base dirs
# ---------------------------------------------------------------------

# .../bheshajpatro/bheshajpatro
PKG_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PKG_DIR.parent

CONFIG_DIR = PKG_DIR / "config"
DATA_DIR = PKG_DIR / "data"
OUTPUT_DIR = PKG_DIR / "output"
LOGS_DIR = PKG_DIR / "logs"

# ---------------------------------------------------------------------
# Engine-specific data dirs
# ---------------------------------------------------------------------

# bheshajpatro/data/kconstants/...
KETAKI_DATA_DIR = DATA_DIR / "kconstants"

# bheshajpatro/data/pyswisseph/...
DRIK_DATA_DIR = DATA_DIR / "pyswisseph"

# bheshajpatro/data/userinput/...
INPUT_DATA_DIR = DATA_DIR / "userinput"


# ---------------------------------------------------------------------
# Simple helpers
# ---------------------------------------------------------------------

def config_path(name: str) -> Path:
    return CONFIG_DIR / name


def data_path(name: str) -> Path:
    return DATA_DIR / name


def output_path(name: str) -> Path:
    return OUTPUT_DIR / name


def logs_path(name: str) -> Path:
    return LOGS_DIR / name


def ketaki_data_path(name: str) -> Path:
    return KETAKI_DATA_DIR / name


def drik_data_path(name: str) -> Path:
    return DRIK_DATA_DIR / name

def input_data_path(name: str) -> Path:
    return INPUT_DATA_DIR / name


__all__ = [
    "PKG_DIR",
    "PROJECT_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "OUTPUT_DIR",
    "LOGS_DIR",
    "KETAKI_DATA_DIR",
    "DRIK_DATA_DIR",
    "INPUT_DATA_DIR",
    "config_path",
    "data_path",
    "output_path",
    "logs_path",
    "ketaki_data_path",
    "drik_data_path",
    "input_data_path",
]
