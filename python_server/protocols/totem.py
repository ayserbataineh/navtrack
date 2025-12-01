"""Totem GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.datetime_util import DateTimeUtil


class TotemProtocol(BaseProtocol):
    """Totem GPS tracker protocol (AT07, AT09)."""
    
    @property
    def port(self) -> int:
        return 7005
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"|"]


class TotemMessageHandler(BaseMessageHandler):
    """Message handler for Totem protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Totem GPS message."""
        msg = input_data.data_message.string.strip('|')
        
        # Totem format: $$IMEI|cmd|data...
        if not msg.startswith("$$"):
            return None
        
        parts = msg[2:].split("|")
        if len(parts) < 3:
            return None
        
        # Extract IMEI
        imei = parts[0]
        if imei.isdigit():
            input_data.connection_context.set_device(imei)
        
        return self._parse_location(parts)
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse location data."""
        try:
            # Find GPS data in parts
            lat = None
            lon = None
            speed = None
            heading = None
            msg_date = None
            
            for i, part in enumerate(parts):
                # Coordinate pattern
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
