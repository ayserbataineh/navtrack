"""GPS coordinate utilities."""

import re
import math
from typing import Optional

from ..models.enums import CardinalPoint


class GpsUtil:
    """Utility class for GPS coordinate operations."""
    
    @staticmethod
    def is_valid_latitude(latitude: Optional[float]) -> bool:
        """Check if latitude is valid (-90 to 90)."""
        return latitude is not None and -90 <= latitude <= 90
    
    @staticmethod
    def is_valid_longitude(longitude: Optional[float]) -> bool:
        """Check if longitude is valid (-180 to 180)."""
        return longitude is not None and -180 <= longitude <= 180
    
    @staticmethod
    def convert_dmm_lat_to_decimal(point: str, cardinal_direction: str) -> float:
        """Convert DMM (Degrees Decimal Minutes) latitude to decimal degrees."""
        return GpsUtil._convert_dmm_to_decimal(r"(\d+)(\d\d.\d+)", point, cardinal_direction)
    
    @staticmethod
    def convert_dmm_long_to_decimal(point: str, cardinal_direction: str) -> float:
        """Convert DMM (Degrees Decimal Minutes) longitude to decimal degrees."""
        return GpsUtil._convert_dmm_to_decimal(r"(\d+)(\d\d.\d+)", point, cardinal_direction)
    
    @staticmethod
    def _convert_dmm_to_decimal(pattern: str, point: str, cardinal_direction: str) -> float:
        """Convert DMM to decimal degrees."""
        match = re.search(pattern, point)
        if not match:
            raise ValueError(f"Invalid coordinate format: {point}")
        
        multiplier = -1 if cardinal_direction in ("S", "W") else 1
        degrees = float(match.group(1))
        minutes = float(match.group(2)) / 60
        
        return round((degrees + minutes) * multiplier, 6)
    
    @staticmethod
    def convert_dms_to_decimal(pattern: str, point: str, cardinal_direction: str) -> float:
        """Convert DMS (Degrees Minutes Seconds) to decimal degrees."""
        match = re.search(pattern, point)
        if not match:
            raise ValueError(f"Invalid coordinate format: {point}")
        
        multiplier = -1 if cardinal_direction in ("S", "W") else 1
        degrees = float(match.group(1))
        minutes = float(match.group(2)) / 60
        seconds = float(match.group(3)) / 3600
        
        return round((degrees + minutes + seconds) * multiplier, 6)
    
    @staticmethod
    def convert_dmm_to_decimal_with_cardinal(
        degrees: float, 
        minutes: float, 
        cardinal_point: CardinalPoint
    ) -> float:
        """Convert DMM to decimal with CardinalPoint enum."""
        multiplier = -1 if cardinal_point in (CardinalPoint.SOUTH, CardinalPoint.WEST) else 1
        return round((degrees + minutes / 60) * multiplier, 6)
    
    @staticmethod
    def convert_string_to_decimal(value: str, cardinal_direction: str) -> float:
        """Convert string coordinate to decimal degrees."""
        multiplier = -1 if cardinal_direction in ("S", "W") else 1
        return float(value) * multiplier
