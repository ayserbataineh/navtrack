"""Queclink GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.datetime_util import DateTimeUtil
from ..models.enums import DateFormat


class QueclinkProtocol(BaseProtocol):
    """Queclink GPS tracker protocol (GL200, GL300, GL500, GV200, GV300, etc.)."""
    
    @property
    def port(self) -> int:
        return 7008
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"$"]


class QueclinkMessageHandler(BaseMessageHandler):
    """Message handler for Queclink protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Queclink GPS message."""
        msg = input_data.data_message.string.strip()
        
        # Queclink messages start with +RESP: or +BUFF:
        if not (msg.startswith("+RESP:") or msg.startswith("+BUFF:")):
            return None
        
        # Remove prefix
        msg = msg[6:] if msg.startswith("+RESP:") else msg[6:]
        
        parts = msg.split(",")
        if len(parts) < 3:
            return None
        
        # Message type is first field
        msg_type = parts[0]
        
        # IMEI is typically in position 2
        if len(parts) > 2 and parts[2].isdigit():
            input_data.connection_context.set_device(parts[2])
        
        # Parse based on message type
        if msg_type in ("GTFRI", "GTGEO", "GTSOS", "GTRTL"):
            return self._parse_location(parts)
        elif msg_type == "GTHBD":
            return self._handle_heartbeat(input_data, parts)
        
        return None
    
    def _parse_location(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse location report message."""
        try:
            # Standard format: TYPE,PROTO,IMEI,...,SATS,LAT,LON,SPEED,HEADING,ALT,...,DATE
            # Field positions vary by message type and protocol version
            
            # Find GPS data - look for patterns
            lat = None
            lon = None
            speed = None
            heading = None
            altitude = None
            satellites = None
            msg_date = None
            
            for i, part in enumerate(parts):
                if not part:
                    continue
                
                # Coordinate pattern
                if re.match(r'^-?\d+\.\d{5,}$', part):
                    val = float(part)
                    if lat is None and -90 <= val <= 90:
                        lat = val
                    elif lon is None and -180 <= val <= 180:
                        lon = val
                
                # Date pattern (YYYYMMDDHHMMSS)
                elif re.match(r'^\d{14}$', part) and msg_date is None:
                    try:
                        msg_date = DateTimeUtil.convert(
                            DateFormat.YYYYMMDDHHMMSS, part
                        )
                    except Exception:
                        pass
            
            # Try structured parsing for GTFRI format
            if lat is None and len(parts) > 15:
                return self._parse_gtfri(parts)
            
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
    
    def _parse_gtfri(self, parts: List[str]) -> Optional[DeviceMessage]:
        """Parse GTFRI (Fixed Report Information) message."""
        try:
            # GTFRI format varies, but common positions:
            # Index 6: Accuracy
            # Index 7: Speed
            # Index 8: Heading
            # Index 9: Altitude
            # Index 10: Longitude
            # Index 11: Latitude
            # Index 12: GPS Date
            # Index 13: MCC
            # etc.
            
            if len(parts) < 15:
                return None
            
            # Try common GTFRI format
            speed = int(float(parts[7])) if parts[7] else None
            heading = int(float(parts[8])) if parts[8] else None
            altitude = int(float(parts[9])) if parts[9] else None
            longitude = float(parts[10]) if parts[10] else None
            latitude = float(parts[11]) if parts[11] else None
            
            msg_date = None
            if parts[12] and len(parts[12]) >= 14:
                try:
                    msg_date = DateTimeUtil.convert(
                        DateFormat.YYYYMMDDHHMMSS, parts[12][:14]
                    )
                except Exception:
                    pass
            
            if latitude is None or longitude is None:
                return None
            
            return DeviceMessage(
                date=msg_date,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                altitude=altitude,
                valid=True
            )
            
        except Exception:
            return None
    
    def _handle_heartbeat(
        self, 
        input_data: MessageInput, 
        parts: List[str]
    ) -> Optional[DeviceMessage]:
        """Handle heartbeat message."""
        # Send heartbeat acknowledgment
        if len(parts) > 2:
            input_data.connection_context.set_device(parts[2])
            input_data.write_string("+SACK:GTHBD$")
        return None
