"""Speed conversion utilities."""

from typing import Optional


class SpeedUtil:
    """Utility class for speed conversions."""
    
    @staticmethod
    def knots_to_kph(knots: float) -> Optional[int]:
        """Convert knots to kilometers per hour."""
        if knots is None:
            return None
        kph = knots * 1.852
        # Clamp to short range
        if kph < -32768:
            return -32768
        if kph > 32767:
            return 32767
        return round(kph)
    
    @staticmethod
    def mph_to_kph(mph: float) -> Optional[int]:
        """Convert miles per hour to kilometers per hour."""
        if mph is None:
            return None
        return round(mph * 1.60934)
    
    @staticmethod
    def kph_to_knots(kph: float) -> Optional[float]:
        """Convert kilometers per hour to knots."""
        if kph is None:
            return None
        return round(kph / 1.852, 2)
