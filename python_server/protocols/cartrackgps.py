"""CarTrackGPS GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class CarTrackGPSProtocol(BaseProtocol):
    """CarTrackGPS GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7033
    
    @property
    def message_start(self) -> bytes:
        return b"$$"


class CarTrackGPSMessageHandler(BaseMessageHandler):
    """Message handler for CarTrackGPS protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        parts = input_data.data_message.comma_split
        if len(parts) < 5:
            return None
        
        for part in parts[:3]:
            clean = part.lstrip('$')
            if clean.isdigit() and len(clean) >= 10:
                input_data.connection_context.set_device(clean)
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
