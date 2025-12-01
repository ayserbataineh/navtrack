"""TkStar GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class TkStarProtocol(BaseProtocol):
    """TkStar GPS tracker protocol (TK905, TK915, TK905B, etc.)."""
    
    @property
    def port(self) -> int:
        return 7011
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"#"]


class TkStarMessageHandler(BaseMessageHandler):
    """Message handler for TkStar protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse TkStar GPS message."""
        msg = input_data.data_message.string.strip().rstrip('#')
        
        # TkStar messages start with *XX, where XX is manufacturer code
        if not msg.startswith("*"):
            return None
        
        # Remove prefix and split
        parts = msg[1:].split(",")
        if len(parts) < 2:
            return None
        
        # Extract IMEI (second field)
        if len(parts) > 1:
            # IMEI may have prefix letters
            imei = re.sub(r'^[A-Za-z]+', '', parts[1])
            if imei.isdigit():
                input_data.connection_context.set_device(imei)
        
        # Get command type
        cmd = parts[2] if len(parts) > 2 else ""
        
        if cmd == "V1":
            return self._parse_location_v1(parts)
        elif cmd == "V0":
            # No GPS fix
            return None
        
        # Try generic location parsing
        return self._parse_location_generic(parts)
    
    def _parse_location_v1(self, parts: List[str]) -> Optional[DeviceMessage]:
        """
        Parse V1 location message.
        
        Format: *MAKER,IMEI,V1,TIME,VALID,LAT,LAT_DIR,LON,LON_DIR,SPEED,HEADING,DATE,...
        """
        try:
            if len(parts) < 14:
                return None
            
            # Time (HHMMSS)
            time_str = parts[3]
            
            # Validity
            valid = parts[4] == 'A'
            
            # Latitude (DDMM.MMMM)
            lat = GpsUtil.convert_dmm_lat_to_decimal(parts[5], parts[6])
            
            # Longitude (DDDMM.MMMM)
            lon = GpsUtil.convert_dmm_long_to_decimal(parts[7], parts[8])
            
            # Speed (knots)
            speed = SpeedUtil.knots_to_kph(float(parts[9])) if parts[9] else None
            
            # Heading
            heading = int(float(parts[10])) if parts[10] else None
            
            # Date (DDMMYY)
            date_str = parts[11]
            
            # Combine time and date
            msg_date = DateTimeUtil.convert(
                DateFormat.HHMMSS_SS_DDMMYY,
                time_str + ".0",
                date_str
            )
            
            return DeviceMessage(
                date=msg_date,
                valid=valid,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading
            )
            
        except Exception:
            return None
    
    def _parse_location_generic(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse generic TkStar location message."""
        try:
            lat = None
            lon = None
            speed = None
            heading = None
            msg_date = None
            valid = None
            
            for i, part in enumerate(parts):
                if not part:
                    continue
                
                # Coordinate in DMM format
                if re.match(r'^\d{3,4}\.\d+$', part):
                    if i + 1 < len(parts):
                        direction = parts[i + 1]
                        if direction in ('N', 'S'):
                            lat = GpsUtil.convert_dmm_lat_to_decimal(part, direction)
                        elif direction in ('E', 'W'):
                            lon = GpsUtil.convert_dmm_long_to_decimal(part, direction)
                
                # Validity
                elif part in ('A', 'V'):
                    valid = part == 'A'
            
            if lat is None or lon is None:
                return None
            
            return DeviceMessage(
                date=msg_date,
                valid=valid,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading
            )
            
        except Exception:
            return None
