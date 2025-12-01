"""Suntech GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class SuntechProtocol(BaseProtocol):
    """Suntech GPS tracker protocol (ST300, ST310, ST340, ST940, etc.)."""
    
    @property
    def port(self) -> int:
        return 7010
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r"]


class SuntechMessageHandler(BaseMessageHandler):
    """Message handler for Suntech protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Suntech GPS message."""
        msg = input_data.data_message.string.strip()
        parts = msg.split(";")
        
        if len(parts) < 5:
            return None
        
        # First part contains device info
        header = parts[0].split(":")
        if len(header) >= 2:
            device_id = header[1] if header[1].isdigit() else header[0]
            input_data.connection_context.set_device(device_id)
        
        return self._parse_location(parts)
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse location data from Suntech message."""
        try:
            lat = None
            lon = None
            speed = None
            heading = None
            msg_date = None
            
            for part in parts:
                # Try to parse as coordinate
                if re.match(r'^-?\d+\.\d+$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
                
                # Try to parse as date (YYYYMMDD;HHMMSS)
                elif re.match(r'^\d{8}$', part):
                    date_str = part
                elif re.match(r'^\d{6}$', part) and len(parts) > 5:
                    time_str = part
            
            if lat is None or lon is None:
                return None
            
            return DeviceMessage(
                date=msg_date,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading,
                valid=True
            )
        except Exception:
            return None
