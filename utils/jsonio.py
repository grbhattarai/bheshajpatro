# bheshajpatro/utils/jsonio.py

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Dict, Optional


# ================================================================
# JSON Reader
# ================================================================

def read_json(path: str | Path) -> Optional[Any]:
    """
    Safely read JSON from a file.

    Returns:
        Parsed JSON object, or None if file missing or failed to parse.
    """
    p = Path(path)
    if not p.exists():
        return None

    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        warnings.warn(f"[jsonio] Failed to read JSON {path}: {e}")
        return None


# ================================================================
# JSON Writer (atomic)
# ================================================================

def _atomic_write_json(p: Path, data: Any, *, indent=2, ensure_ascii=False) -> None:
    """
    Internal helper: write JSON atomically using temporary file.
    """
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp = p.with_name(p.name + ".tmp")

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

    tmp.replace(p)  # atomic on POSIX, safe fallback on Windows


def write_json(path: str | Path, data: Any, *,
               indent: int = 2, ensure_ascii: bool = False) -> bool:
    """
    Write JSON with atomic replace.
    Returns True on success, False on failure.
    """
    try:
        _atomic_write_json(Path(path), data,
                           indent=indent,
                           ensure_ascii=ensure_ascii)
        return True
    except Exception as e:
        warnings.warn(f"[jsonio] Failed to write {path}: {e}")
        return False


def write_json_atomic(path: str | Path, data: Any) -> None:
    """
    Backwards-compatible wrapper.
    Always overwrites atomically using UTF-8.
    """
    _atomic_write_json(Path(path), data,
                       indent=2,
                       ensure_ascii=False)


# ================================================================
# JSON Lines Writer
# ================================================================

def append_json_line(path: str | Path, record: Dict[str, Any]) -> None:
    """
    Append one JSON object per line (newline-delimited JSON).
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ================================================================
# Utility
# ================================================================

def exists_nonempty(path: str | Path) -> bool:
    """
    Return True if the file exists and is non-empty.
    """
    p = Path(path)
    return p.exists() and p.stat().st_size > 0
