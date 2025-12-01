"""Tzone GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.gprmc import GPRMC


class TzoneProtocol(BaseProtocol):
    """Tzone GPS tracker protocol (AVL01, AVL02, AVL05, AVL08, etc.)."""
    
    @property
    def port(self) -> int:
        return 7006
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n"]


class TzoneMessageHandler(BaseMessageHandler):
    """Message handler for Tzone protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Tzone GPS message."""
        msg = input_data.data_message.string.strip()
        
        # Find IMEI
        imei_match = re.search(r'(\d{15})', msg)
        if imei_match:
            input_data.connection_context.set_device(imei_match.group(1))
        
        # Look for GPRMC
        if "GPRMC" in msg:
            gprmc_match = re.search(r'\$?GPRMC[^*]+', msg)
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
        
        return self._parse_standard(input_data)
    
    def _parse_standard(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse standard format."""
        parts = input_data.data_message.comma_split
        
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
