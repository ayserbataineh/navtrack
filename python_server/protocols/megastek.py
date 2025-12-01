"""Megastek GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.datetime_util import DateTimeUtil
from ..helpers.gprmc import GPRMC


class MegastekProtocol(BaseProtocol):
    """Megastek GPS tracker protocol (MT60, MT68, MT90, GT06, etc.)."""
    
    @property
    def port(self) -> int:
        return 7004
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n", b"!"]


class MegastekMessageHandler(BaseMessageHandler):
    """Message handler for Megastek protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Megastek GPS message."""
        msg = input_data.data_message.string.strip()
        
        # Try GPRMC format first
        if "$GPRMC" in msg:
            return self._parse_gprmc(input_data, msg)
        
        # Try comma-separated format
        return self._parse_standard(input_data)
    
    def _parse_gprmc(self, input_data: MessageInput, msg: str) -> Optional[DeviceMessage]:
        """Parse GPRMC-based message."""
        # Find IMEI (usually before GPRMC)
        imei_match = re.search(r'(\d{15})', msg)
        if imei_match:
            input_data.connection_context.set_device(imei_match.group(1))
        
        # Find GPRMC sentence
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
    
    def _parse_standard(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse standard comma-separated format."""
        parts = input_data.data_message.comma_split
        
        if len(parts) < 10:
            return None
        
        # Extract IMEI (usually first field or after STX)
        for part in parts[:3]:
            if part.isdigit() and len(part) >= 10:
                input_data.connection_context.set_device(part)
                break
        
        # Try to find coordinates
        lat = None
        lon = None
        
        for i, part in enumerate(parts):
            if re.match(r'^\d{4}\.\d+$', part):
                if i + 1 < len(parts):
                    direction = parts[i + 1]
                    if direction in ('N', 'S'):
                        lat = GpsUtil.convert_dmm_lat_to_decimal(part, direction)
                    elif direction in ('E', 'W'):
                        lon = GpsUtil.convert_dmm_long_to_decimal(part, direction)
        
        if lat is None or lon is None:
            return None
        
        return DeviceMessage(
            latitude=lat,
            longitude=lon,
            valid=True
        )
