from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return project_root() / "bheshajpatro" / "data"


def input_data_dir() -> Path:
    return data_dir() / "inputdata"


def input_data_path(filename: str) -> Path:
    return input_data_dir() / filename