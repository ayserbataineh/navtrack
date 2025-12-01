"""GlobalSat GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.datetime_util import DateTimeUtil


class GlobalSatProtocol(BaseProtocol):
    """GlobalSat GPS tracker protocol (TR-151, TR-203, TR-206, etc.)."""
    
    @property
    def port(self) -> int:
        return 7038
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"!"]


class GlobalSatMessageHandler(BaseMessageHandler):
    """Message handler for GlobalSat protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse GlobalSat GPS message."""
        return self.parse_with_handlers(
            input_data,
            self._parse_format_0,
            self._parse_format_alternative
        )
    
    def _parse_format_0(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse format 0 location message."""
        # Send ACK
        input_data.write(b"ACK\r")
        
        pattern = (
            r"(\d{15}),"          # IMEI
            r"(.*),"              # skip
            r"(\d),"              # GPS fix
            r"(\d{2})(\d{2})(\d{2}),"  # DD MM YY
            r"(\d{2})(\d{2})(\d{2}),"  # HH MM SS
            r"(E|W)(\d+\.\d+),"   # Longitude
            r"(N|S)(\d+\.\d+),"   # Latitude
            r"(\d+),"             # Altitude
            r"(.*?),"             # Speed
            r"(\d+),"             # Heading
            r"(\d+),"             # Satellites
            r"(.*?)"              # HDOP
        )
        
        match = re.match(pattern, input_data.data_message.string)
        
        if not match:
            return None
        
        input_data.connection_context.set_device(match.group(1))
        
        msg_date = DateTimeUtil.new(
            match.group(6),  # year
            match.group(5),  # month
            match.group(4),  # day
            match.group(7),  # hour
            match.group(8),  # minute
            match.group(9)   # second
        )
        
        valid = match.group(3) != "1"
        longitude = GpsUtil.convert_dmm_long_to_decimal(
            match.group(11), match.group(10)
        )
        latitude = GpsUtil.convert_dmm_lat_to_decimal(
            match.group(13), match.group(12)
        )
        
        altitude = self._safe_int(match.group(14))
        speed = SpeedUtil.knots_to_kph(self._safe_float(match.group(15)))
        heading = self._safe_int(match.group(16))
        satellites = self._safe_int(match.group(17))
        hdop = self._safe_float(match.group(18))
        
        return DeviceMessage(
            date=msg_date,
            valid=valid,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            speed=speed,
            heading=heading,
            satellites=satellites,
            hdop=hdop
        )
    
    def _parse_format_alternative(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse alternative format location message."""
        pattern = (
            r"(\d+),"             # IMEI
            r"(\d),"              # skip
            r"(\d+),"             # GPS fix
            r"(\d{2})(\d{2})(\d{2}),"  # DD MM YY
            r"(\d{2})(\d{2})(\d{2}),"  # HH MM SS
            r"(E|W)(\d+\.\d+),"   # Longitude
            r"(N|S)(\d+\.\d+),"   # Latitude
            r"(\d+\.\d+),"        # Altitude
            r"(\d+\.\d+),"        # Speed
            r"(.*?|),"            # Heading
            r"(\d+)"              # Satellites
            r"(,(\d+\.\d+)|)"     # HDOP (optional)
        )
        
        match = re.match(pattern, input_data.data_message.string)
        
        if not match:
            return None
        
        input_data.connection_context.set_device(match.group(1))
        
        msg_date = DateTimeUtil.new(
            match.group(6),  # year
            match.group(5),  # month
            match.group(4),  # day
            match.group(7),  # hour
            match.group(8),  # minute
            match.group(9)   # second
        )
        
        valid = match.group(2) != "1"
        longitude = GpsUtil.convert_dmm_long_to_decimal(
            match.group(11), match.group(10)
        )
        latitude = GpsUtil.convert_dmm_lat_to_decimal(
            match.group(13), match.group(12)
        )
        
        altitude = self._safe_int(match.group(14))
        speed = SpeedUtil.knots_to_kph(self._safe_float(match.group(15)))
        heading = self._safe_int(match.group(16)) if match.group(16) else None
        satellites = self._safe_int(match.group(17))
        hdop = self._safe_float(match.group(19)) if match.group(19) else None
        
        return DeviceMessage(
            date=msg_date,
            valid=valid,
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            speed=speed,
            heading=heading,
            satellites=satellites,
            hdop=hdop
        )
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int."""
        try:
            return int(float(value)) if value else None
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float."""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
