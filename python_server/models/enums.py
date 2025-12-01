"""Enums for GPS tracking server."""

from enum import Enum, auto


class CardinalPoint(Enum):
    """Cardinal direction points."""
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


class DateFormat(Enum):
    """Date format types for parsing."""
    HHMMSS_SS_DDMMYY = auto()
    YYMMDDHHMMSS = auto()
    YYYYMMDDHHMMSS = auto()
    DDMMYYHHMMSS = auto()
    DDMMYY_HHMMSS = auto()


class GpsFormat(Enum):
    """GPS coordinate format types."""
    DDDMMmmmm = auto()
