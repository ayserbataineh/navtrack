"""ATrack GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class ATrackProtocol(BaseProtocol):
    """ATrack GPS tracker protocol (AL1, AK1, AK11, AU5, AT5, etc.)."""
    
    @property
    def port(self) -> int:
        return 7061


class ATrackMessageHandler(BaseMessageHandler):
    """Message handler for ATrack protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        msg = input_data.data_message.string.strip()
        
        # ATrack format: @P,IMEI,TIME,MSGTYPE,LAT,LON,...
        if not msg.startswith("@P"):
            return None
        
        parts = msg[3:].split(",")
        if len(parts) < 6:
            return None
        
        # IMEI
        if parts[0].isdigit():
            input_data.connection_context.set_device(parts[0])
        
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
                
                # Date pattern (Unix timestamp)
                elif re.match(r'^\d{10}$', part) and msg_date is None:
                    try:
                        from datetime import datetime
                        msg_date = datetime.utcfromtimestamp(int(part))
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
