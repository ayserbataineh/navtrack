"""Meiligao GPS protocol implementation."""

import struct
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.datetime_util import DateTimeUtil
from ..helpers.gprmc import GPRMC


class MeiligaoProtocol(BaseProtocol):
    """Meiligao GPS tracker protocol (GT30, GT60, VT300, VT310, etc.)."""
    
    @property
    def port(self) -> int:
        return 7003
    
    @property
    def message_start(self) -> bytes:
        return b"$$"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n"]


class MeiligaoMessageHandler(BaseMessageHandler):
    """Message handler for Meiligao protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Meiligao GPS message."""
        data = input_data.data_message.bytes
        
        if len(data) < 10:
            return None
        
        # Extract device ID (7 bytes after $$)
        if len(data) >= 9:
            device_id = data[2:9].hex()
            input_data.connection_context.set_device(device_id)
        
        # Check for GPRMC data in the message
        msg_str = input_data.data_message.string
        if "$GPRMC" in msg_str:
            return self._parse_gprmc(msg_str)
        
        return self._parse_binary(data)
    
    def _parse_gprmc(self, msg: str) -> Optional[DeviceMessage]:
        """Parse GPRMC sentence from message."""
        import re
        gprmc_match = re.search(r'\$GPRMC[^*]+', msg)
        if gprmc_match:
            gprmc = GPRMC.parse(gprmc_match.group(0))
            if gprmc:
                return DeviceMessage(
                    date=gprmc.datetime,
                    latitude=gprmc.latitude,
                    longitude=gprmc.longitude,
                    speed=gprmc.speed,
                    heading=int(gprmc.heading) if gprmc.heading else None,
                    valid=gprmc.position_status
                )
        return None
    
    def _parse_binary(self, data: bytes) -> Optional[DeviceMessage]:
        """Parse binary position data."""
        # Meiligao binary format varies
        # This is a basic implementation
        return None
