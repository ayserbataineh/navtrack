"""Gosafe GPS protocol implementation."""

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


class GosafeProtocol(BaseProtocol):
    """Gosafe GPS tracker protocol (G1C, G3S, G6S, G737, etc.)."""
    
    @property
    def port(self) -> int:
        return 7022
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"#"]


class GosafeMessageHandler(BaseMessageHandler):
    """Message handler for Gosafe protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Gosafe GPS message."""
        msg = input_data.data_message.string.strip().rstrip('#')
        
        # Format: *GS##,IMEI,CMD,DATA...#
        if not msg.startswith("*GS"):
            return None
        
        parts = msg.split(",")
        if len(parts) < 3:
            return None
        
        # IMEI is second field (may have prefix)
        imei = re.sub(r'^[A-Z]+', '', parts[1])
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
            
            for i, part in enumerate(parts):
                # Decimal coordinates
                if re.match(r'^-?\d+\.\d+$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
                
                # Date pattern
                elif re.match(r'^\d{6}$', part) and msg_date is None:
                    # Look for time in next field
                    if i + 1 < len(parts) and re.match(r'^\d{6}$', parts[i+1]):
                        try:
                            msg_date = DateTimeUtil.convert(
                                DateFormat.DDMMYYHHMMSS,
                                part + parts[i+1]
                            )
                        except Exception:
                            pass
            
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
