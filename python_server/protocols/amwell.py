"""Amwell GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil


class AmwellProtocol(BaseProtocol):
    """Amwell GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7035
    
    @property
    def message_start(self) -> bytes:
        return b"))"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r"]


class AmwellMessageHandler(BaseMessageHandler):
    """Message handler for Amwell protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        msg = input_data.data_message.string.lstrip(')')
        parts = msg.split(",")
        
        if len(parts) < 5:
            return None
        
        for part in parts[:3]:
            if part.isdigit() and len(part) >= 10:
                input_data.connection_context.set_device(part)
                break
        
        lat, lon = None, None
        for i, part in enumerate(parts):
            if re.match(r'^\d{4}\.\d+$', part) and i + 1 < len(parts):
                direction = parts[i + 1]
                if direction in ('N', 'S'):
                    lat = GpsUtil.convert_dmm_lat_to_decimal(part, direction)
                elif direction in ('E', 'W'):
                    lon = GpsUtil.convert_dmm_long_to_decimal(part, direction)
        
        if lat and lon:
            return DeviceMessage(latitude=lat, longitude=lon, valid=True)
        return None
