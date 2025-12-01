"""Fifotrack GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class FifotrackProtocol(BaseProtocol):
    """Fifotrack GPS tracker protocol (A300, A500, A600, Q1, etc.)."""
    
    @property
    def port(self) -> int:
        return 7009
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"##"]


class FifotrackMessageHandler(BaseMessageHandler):
    """Message handler for Fifotrack protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Fifotrack GPS message."""
        msg = input_data.data_message.string.strip()
        
        # Format: $$IMEI,CMD,DATA,...##
        if not msg.startswith("$$"):
            return None
        
        msg = msg[2:].rstrip("#")
        parts = msg.split(",")
        
        if len(parts) < 3:
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
            satellites = None
            altitude = None
            
            # Look for standard position fields
            for i, part in enumerate(parts):
                # Decimal coordinate
                if re.match(r'^-?\d+\.\d{5,}$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
                
                # Date/Time (YYYYMMDDHHMMSS)
                elif re.match(r'^\d{14}$', part) and msg_date is None:
                    try:
                        msg_date = DateTimeUtil.convert(
                            DateFormat.YYYYMMDDHHMMSS, part
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
                altitude=altitude,
                satellites=satellites,
                valid=True
            )
        except Exception:
            return None
