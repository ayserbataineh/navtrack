"""GPRMC sentence parser."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .datetime_util import DateTimeUtil
from .gps_util import GpsUtil
from .speed_util import SpeedUtil
from ..models.enums import DateFormat


@dataclass
class GPRMC:
    """GPRMC (Recommended Minimum Navigation Information) data."""
    
    datetime: datetime
    latitude: float
    longitude: float
    position_status: bool
    speed: Optional[int] = None
    heading: Optional[float] = None
    
    @classmethod
    def parse(cls, input_str: str) -> Optional['GPRMC']:
        """
        Parse GPRMC sentence.
        
        Example input: $GPRMC,102156.000,A,2232.4690,N,11403.6847,E,0.00,,180909,,*15
        """
        pattern = (
            r"(\d{2}\d{2}\d{2}\.\d+),"  # time hhmmss.sss
            r"(A|V),"                     # status
            r"(\d+\.\d+),(N|S),"          # latitude
            r"(\d+\.\d+),(E|W),"          # longitude
            r"(.*?),"                     # speed
            r"(.*?),"                     # heading
            r"(\d{2}\d{2}\d{2})"          # date ddmmyy
        )
        
        match = re.search(pattern, input_str)
        if not match:
            return None
        
        try:
            dt = DateTimeUtil.convert(
                DateFormat.HHMMSS_SS_DDMMYY,
                match.group(1),
                match.group(9)
            )
            
            speed_str = match.group(7)
            speed = None
            if speed_str:
                try:
                    speed = SpeedUtil.knots_to_kph(float(speed_str))
                except ValueError:
                    pass
            
            heading_str = match.group(8)
            heading = None
            if heading_str:
                try:
                    heading = float(heading_str)
                except ValueError:
                    pass
            
            return cls(
                datetime=dt,
                position_status=match.group(2) == "A",
                latitude=GpsUtil.convert_dmm_lat_to_decimal(
                    match.group(3), match.group(4)
                ),
                longitude=GpsUtil.convert_dmm_long_to_decimal(
                    match.group(5), match.group(6)
                ),
                speed=speed,
                heading=heading
            )
        except (ValueError, IndexError):
            return None
