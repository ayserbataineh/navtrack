"""Xirgo GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class XirgoProtocol(BaseProtocol):
    """Xirgo GPS tracker protocol (XT2000, XT4700, XT6000, etc.)."""
    
    @property
    def port(self) -> int:
        return 7024
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"##"]


class XirgoMessageHandler(BaseMessageHandler):
    """Message handler for Xirgo protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Xirgo GPS message."""
        msg = input_data.data_message.string.strip().rstrip('#')
        
        if not msg.startswith("$$"):
            return None
        
        parts = msg[2:].split(",")
        if len(parts) < 5:
            return None
        
        # IMEI is first field
        imei = parts[0]
        if imei.isdigit():
            input_data.connection_context.set_device(imei)
        
        return self._parse_location(parts)
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse location data."""
        try:
            lat = None
            lon = None
            speed = None
            heading = None
            msg_date = None
            
            for part in parts:
                if re.match(r'^-?\d+\.\d+$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
            
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
