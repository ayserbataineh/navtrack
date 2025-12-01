"""ManPower GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class ManPowerProtocol(BaseProtocol):
    """ManPower GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7045


class ManPowerMessageHandler(BaseMessageHandler):
    """Message handler for ManPower protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        parts = input_data.data_message.comma_split
        if len(parts) < 5:
            return None
        
        for part in parts[:3]:
            if part.isdigit() and len(part) >= 10:
                input_data.connection_context.set_device(part)
                break
        
        lat, lon = None, None
        for part in parts:
            if re.match(r'^-?\d+\.\d+$', part):
                val = float(part)
                if lat is None and -90 <= val <= 90:
                    lat = val
                elif lon is None and -180 <= val <= 180:
                    lon = val
        
        if lat and lon:
            return DeviceMessage(latitude=lat, longitude=lon, valid=True)
        return None
