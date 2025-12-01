"""Ruptela GPS protocol implementation."""

import struct
from typing import Optional, List
from datetime import datetime

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class RuptelaProtocol(BaseProtocol):
    """Ruptela GPS tracker protocol (FM-Tco4, FM-Eco4, FM-Pro4, etc.)."""
    
    @property
    def port(self) -> int:
        return 7056


class RuptelaMessageHandler(BaseMessageHandler):
    """Message handler for Ruptela protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        data = input_data.data_message.bytes
        if len(data) < 10:
            return None
        
        return self._parse_binary(input_data, data)
    
    def parse_range(self, input_data: MessageInput) -> Optional[List[DeviceMessage]]:
        """Parse Ruptela packet with multiple records."""
        data = input_data.data_message.bytes
        
        try:
            if len(data) < 10:
                return None
            
            offset = 0
            
            # Packet length (2 bytes)
            length = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2
            
            # IMEI (8 bytes)
            imei = struct.unpack('>Q', data[offset:offset+8])[0]
            input_data.connection_context.set_device(str(imei))
            offset += 8
            
            # Command (1 byte)
            cmd = data[offset]
            offset += 1
            
            if cmd == 0x01:  # Records
                messages = self._parse_records(data, offset)
                if messages:
                    # Send ACK
                    input_data.write(struct.pack('>BH', 0x02, len(messages)))
                return messages
            
            return None
        except Exception:
            return None
    
    def _parse_binary(self, input_data: MessageInput, data: bytes) -> Optional[DeviceMessage]:
        """Parse single binary record."""
        messages = self.parse_range(input_data)
        return messages[0] if messages else None
    
    def _parse_records(self, data: bytes, offset: int) -> Optional[List[DeviceMessage]]:
        """Parse multiple records."""
        try:
            messages = []
            
            # Record count (1 byte)
            count = data[offset]
            offset += 1
            
            for _ in range(count):
                if offset + 30 > len(data):
                    break
                
                # Timestamp (4 bytes)
                timestamp = struct.unpack('>I', data[offset:offset+4])[0]
                msg_date = datetime.utcfromtimestamp(timestamp)
                offset += 4
                
                # Skip priority byte
                offset += 1
                
                # Longitude (4 bytes, divide by 10000000)
                lon = struct.unpack('>i', data[offset:offset+4])[0] / 10000000.0
                offset += 4
                
                # Latitude (4 bytes, divide by 10000000)
                lat = struct.unpack('>i', data[offset:offset+4])[0] / 10000000.0
                offset += 4
                
                # Altitude (2 bytes)
                altitude = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                
                # Heading (2 bytes)
                heading = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                
                # Satellites (1 byte)
                satellites = data[offset]
                offset += 1
                
                # Speed (2 bytes)
                speed = struct.unpack('>H', data[offset:offset+2])[0]
                offset += 2
                
                # Skip IO elements (variable length)
                io_count = data[offset]
                offset += 1 + io_count * 3  # Each IO is ID (1) + value (2)
                
                messages.append(DeviceMessage(
                    date=msg_date,
                    latitude=lat,
                    longitude=lon,
                    altitude=altitude,
                    heading=heading,
                    satellites=satellites,
                    speed=speed,
                    valid=satellites > 0
                ))
            
            return messages if messages else None
        except Exception:
            return None
