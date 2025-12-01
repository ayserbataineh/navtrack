"""VjoyCar GPS protocol implementation."""

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


class VjoyCarProtocol(BaseProtocol):
    """VjoyCar GPS tracker protocol (TK06A, TK10, T18, etc.)."""
    
    @property
    def port(self) -> int:
        return 7020
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n"]


class VjoyCarMessageHandler(BaseMessageHandler):
    """Message handler for VjoyCar protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse VjoyCar GPS message."""
        msg = input_data.data_message.string.strip()
        parts = msg.split(",")
        
        if len(parts) < 5:
            return None
        
        # Find IMEI
        for part in parts[:3]:
            clean = re.sub(r'^[^0-9]+', '', part)
            if clean.isdigit() and len(clean) >= 10:
                input_data.connection_context.set_device(clean)
                break
        
        return self._parse_location(parts)
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse location data."""
        try:
            lat = None
            lon = None
            speed = None
            heading = None
            msg_date = None
            valid = None
            
            for i, part in enumerate(parts):
                # DMM coordinates
                if re.match(r'^\d{4}\.\d+$', part):
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
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading,
                valid=valid
            )
        except Exception:
            return None
