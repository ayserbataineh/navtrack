"""Eelink GPS protocol implementation."""

import struct
from typing import Optional, List
from datetime import datetime

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class EelinkProtocol(BaseProtocol):
    """Eelink GPS tracker protocol (TK115, TK116, TK119, GPT18, etc.)."""
    
    @property
    def port(self) -> int:
        return 7021
    
    @property
    def message_start(self) -> bytes:
        return b"\x67\x67"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b""]


class EelinkMessageHandler(BaseMessageHandler):
    """Message handler for Eelink protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Eelink GPS message."""
        data = input_data.data_message.bytes
        
        if len(data) < 7:
            return None
        
        # Message type at byte 2
        msg_type = data[2]
        
        if msg_type == 0x01:  # Login
            return self._handle_login(input_data, data)
        elif msg_type == 0x12:  # GPS data
            return self._parse_gps(input_data, data)
        elif msg_type == 0x13:  # Heartbeat
            return self._handle_heartbeat(input_data, data)
        
        return None
    
    def _handle_login(self, input_data: MessageInput, data: bytes) -> Optional[DeviceMessage]:
        """Handle login message."""
        if len(data) >= 15:
            # IMEI at bytes 7-14
            imei = data[7:15].hex()
            input_data.connection_context.set_device(imei)
            # Send login response
            input_data.write(b"\x67\x67\x01\x00\x05\x01\x00")
        return None
    
    def _parse_gps(self, input_data: MessageInput, data: bytes) -> Optional[DeviceMessage]:
        """Parse GPS data message."""
        try:
            if len(data) < 25:
                return None
            
            offset = 7
            
            # Timestamp (4 bytes)
            timestamp = struct.unpack('>I', data[offset:offset+4])[0]
            msg_date = datetime.utcfromtimestamp(timestamp)
            offset += 4
            
            # Latitude (4 bytes, divide by 1800000)
            lat_raw = struct.unpack('>i', data[offset:offset+4])[0]
            latitude = lat_raw / 1800000.0
            offset += 4
            
            # Longitude (4 bytes, divide by 1800000)
            lon_raw = struct.unpack('>i', data[offset:offset+4])[0]
            longitude = lon_raw / 1800000.0
            offset += 4
            
            # Speed (1 byte)
            speed = data[offset]
            offset += 1
            
            # Heading (2 bytes)
            heading = struct.unpack('>H', data[offset:offset+2])[0]
            
            return DeviceMessage(
                date=msg_date,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                valid=True
            )
        except Exception:
            return None
    
    def _handle_heartbeat(self, input_data: MessageInput, data: bytes) -> Optional[DeviceMessage]:
        """Handle heartbeat message."""
        input_data.write(b"\x67\x67\x13\x00\x05\x01\x00")
        return None
