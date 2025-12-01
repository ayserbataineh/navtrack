"""Meitrack GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class MeitrackProtocol(BaseProtocol):
    """Meitrack GPS tracker protocol (T333, T366, T399, MVT340, MVT380, etc.)."""
    
    @property
    def port(self) -> int:
        return 7001
    
    @property
    def message_start(self) -> bytes:
        return b"$$"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n"]


class MeitrackMessageHandler(BaseMessageHandler):
    """Message handler for Meitrack protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Meitrack GPS message."""
        msg = input_data.data_message.string
        
        # Remove $$ prefix if present
        if msg.startswith("$$"):
            msg = msg[2:]
        
        # Parse command type
        parts = msg.split(",")
        if len(parts) < 3:
            return None
        
        # Extract IMEI (first field after length)
        try:
            # Format: LEN,IMEI,CMD,...
            imei = parts[1] if parts[1].isdigit() else parts[0]
            input_data.connection_context.set_device(imei)
        except Exception:
            return None
        
        # Parse based on command type
        return self._parse_location(parts)
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """
        Parse location data.
        
        Format varies but generally:
        $$LEN,IMEI,CMD,EVENT,LAT,LON,DATE,TIME,VALID,SATS,GSM,SPEED,HEADING,...
        """
        try:
            # Find position data - look for coordinates pattern
            lat = None
            lon = None
            msg_date = None
            speed = None
            heading = None
            satellites = None
            valid = None
            
            for i, part in enumerate(parts):
                # Latitude pattern (decimal degrees, possibly with sign)
                if re.match(r'^-?\d+\.\d+$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
                
                # Date pattern (YYMMDDHHMMSS or YYYYMMDDHHMMSS)
                elif re.match(r'^\d{12,14}$', part) and msg_date is None:
                    try:
                        if len(part) == 14:
                            msg_date = DateTimeUtil.convert(
                                DateFormat.YYYYMMDDHHMMSS, part
                            )
                        else:
                            msg_date = DateTimeUtil.convert(
                                DateFormat.YYMMDDHHMMSS, part
                            )
                    except Exception:
                        pass
                
                # Validity indicator
                elif part in ('A', 'V') and valid is None:
                    valid = part == 'A'
            
            # Try structured parsing if pattern matching failed
            if lat is None or lon is None:
                return self._parse_structured(parts)
            
            return DeviceMessage(
                date=msg_date,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading,
                satellites=satellites,
                valid=valid
            )
            
        except Exception:
            return None
    
    def _parse_structured(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse with known field positions for common Meitrack formats."""
        try:
            # AAA format: $$LEN,IMEI,AAA,EVENT,LAT,LON,DATE,TIME,VALID,SATS,...
            if len(parts) >= 10 and parts[2] == 'AAA':
                lat = float(parts[4])
                lon = float(parts[5])
                
                # Combine date and time
                date_str = parts[6] + parts[7]
                msg_date = DateTimeUtil.convert(DateFormat.YYMMDDHHMMSS, date_str)
                
                valid = parts[8] == 'A'
                satellites = int(parts[9]) if parts[9].isdigit() else None
                
                speed = None
                if len(parts) > 11:
                    try:
                        speed = int(float(parts[11]))
                    except ValueError:
                        pass
                
                heading = None
                if len(parts) > 12:
                    try:
                        heading = int(float(parts[12]))
                    except ValueError:
                        pass
                
                return DeviceMessage(
                    date=msg_date,
                    latitude=lat,
                    longitude=lon,
                    valid=valid,
                    satellites=satellites,
                    speed=speed,
                    heading=heading
                )
        except Exception:
            pass
        
        return None
