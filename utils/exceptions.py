# bheshajpatro/utils/exceptions.py
from __future__ import annotations

class PanchangaError(Exception):
    """Base class for all Panchanga-related exceptions."""
    pass


class ValidationError(PanchangaError):
    """Invalid user-provided data."""
    pass


class MissingDataError(PanchangaError):
    """Required data file is missing."""
    pass


class TimezoneError(PanchangaError):
    """Timezone parsing or lookup failed."""
    pass


class EngineError(PanchangaError):
    """Failure inside Ketaki or Drik engine."""
    pass
