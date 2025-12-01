"""Teltonika GPS protocol implementation."""

import struct
from typing import Optional, List
from datetime import datetime

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class TeltonikaProtocol(BaseProtocol):
    """Teltonika GPS tracker protocol (FMB920, FMB140, FMM130, etc.)."""
    
    @property
    def port(self) -> int:
        return 7002
    
    def get_message_length(self, buffer: bytes, bytes_read: int) -> Optional[int]:
        """Get message length for Teltonika binary protocol."""
        if bytes_read > 7:
            # Check for data packet (starts with 0x00000000)
            if buffer[0:4] == b'\x00\x00\x00\x00':
                # Data length is in bytes 4-8 (big-endian)
                data_length = struct.unpack('>I', buffer[4:8])[0]
                # Total: 4 (prefix) + 4 (data length field) + data_length + 4 (CRC)
                return 4 + 4 + data_length + 4
        
        return None


class TeltonikaMessageHandler(BaseMessageHandler):
    """Message handler for Teltonika protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Teltonika GPS message."""
        return self.parse_with_handlers(
            input_data,
            self._parse_imei,
            self._parse_data
        )
    
    def parse_range(self, input_data: MessageInput) -> Optional[List[DeviceMessage]]:
        """Parse Teltonika data packet with multiple records."""
        data = input_data.data_message.bytes
        
        # Check for IMEI message (short message, just IMEI length + IMEI)
        if len(data) < 20 and len(data) >= 2:
            return self._handle_imei(input_data, data)
        
        # Check for data packet
        if len(data) > 8 and data[0:4] == b'\x00\x00\x00\x00':
            return self._parse_data_packet(input_data, data)
        
        return None
    
    def _parse_imei(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse IMEI authentication message."""
        data = input_data.data_message.bytes
        
        if len(data) >= 2:
            imei_length = struct.unpack('>H', data[0:2])[0]
            if len(data) >= 2 + imei_length:
                imei = data[2:2 + imei_length].decode('ascii', errors='ignore')
                input_data.connection_context.set_device(imei)
                # Send acknowledgment (0x01 = accept)
                input_data.write(b'\x01')
        
        return None
    
    def _parse_data(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse single data record (uses parse_range internally)."""
        messages = self.parse_range(input_data)
        return messages[0] if messages else None
    
    def _handle_imei(self, input_data: MessageInput, data: bytes) -> Optional[List[DeviceMessage]]:
        """Handle IMEI authentication."""
        if len(data) >= 2:
            imei_length = struct.unpack('>H', data[0:2])[0]
            if len(data) >= 2 + imei_length:
                imei = data[2:2 + imei_length].decode('ascii', errors='ignore')
                input_data.connection_context.set_device(imei)
                input_data.write(b'\x01')
        return None
    
    def _parse_data_packet(
        self, 
        input_data: MessageInput, 
        data: bytes
    ) -> Optional[List[DeviceMessage]]:
        """Parse Teltonika data packet with AVL records."""
        try:
            # Skip preamble (4 bytes) and data length (4 bytes)
            offset = 8
            
            # Codec ID
            codec_id = data[offset]
            offset += 1
            
            # Number of records
            record_count = data[offset]
            offset += 1
            
            messages = []
            
            for _ in range(record_count):
                msg, offset = self._parse_avl_record(data, offset, codec_id)
                if msg:
                    messages.append(msg)
            
            # Send acknowledgment (number of records received)
            if messages:
                input_data.write(struct.pack('>I', len(messages)))
            
            return messages if messages else None
            
        except Exception:
            return None
    
    def _parse_avl_record(
        self, 
        data: bytes, 
        offset: int, 
        codec_id: int
    ) -> tuple:
        """Parse a single AVL data record."""
        try:
            # Timestamp (8 bytes, milliseconds since epoch)
            timestamp_ms = struct.unpack('>Q', data[offset:offset + 8])[0]
            timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000)
            offset += 8
            
            # Priority (1 byte)
            priority = data[offset]
            offset += 1
            
            # GPS data
            # Longitude (4 bytes, signed, divide by 10000000)
            longitude = struct.unpack('>i', data[offset:offset + 4])[0] / 10000000.0
            offset += 4
            
            # Latitude (4 bytes, signed, divide by 10000000)
            latitude = struct.unpack('>i', data[offset:offset + 4])[0] / 10000000.0
            offset += 4
            
            # Altitude (2 bytes, signed)
            altitude = struct.unpack('>h', data[offset:offset + 2])[0]
            offset += 2
            
            # Heading/Angle (2 bytes, unsigned)
            heading = struct.unpack('>H', data[offset:offset + 2])[0]
            offset += 2
            
            # Satellites (1 byte)
            satellites = data[offset]
            offset += 1
            
            # Speed (2 bytes, unsigned, km/h)
            speed = struct.unpack('>H', data[offset:offset + 2])[0]
            offset += 2
            
            # Parse IO elements based on codec
            offset = self._skip_io_elements(data, offset, codec_id)
            
            msg = DeviceMessage(
                date=timestamp,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                heading=heading,
                satellites=satellites,
                speed=speed,
                valid=satellites > 0
            )
            
            return msg, offset
            
        except Exception:
            return None, offset
    
    def _skip_io_elements(self, data: bytes, offset: int, codec_id: int) -> int:
        """Skip over IO elements in the data."""
        try:
            if codec_id == 0x08:  # Codec 8
                # Event IO ID (1 byte)
                offset += 1
                # Total IO count (1 byte)
                offset += 1
                
                # 1-byte IO elements
                count = data[offset]
                offset += 1
                offset += count * 2  # ID (1) + value (1)
                
                # 2-byte IO elements
                count = data[offset]
                offset += 1
                offset += count * 3  # ID (1) + value (2)
                
                # 4-byte IO elements
                count = data[offset]
                offset += 1
                offset += count * 5  # ID (1) + value (4)
                
                # 8-byte IO elements
                count = data[offset]
                offset += 1
                offset += count * 9  # ID (1) + value (8)
                
            elif codec_id == 0x8E:  # Codec 8 Extended
                # Event IO ID (2 bytes)
                offset += 2
                # Total IO count (2 bytes)
                offset += 2
                
                # 1-byte IO elements
                count = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
                offset += count * 3  # ID (2) + value (1)
                
                # 2-byte IO elements
                count = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
                offset += count * 4  # ID (2) + value (2)
                
                # 4-byte IO elements
                count = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
                offset += count * 6  # ID (2) + value (4)
                
                # 8-byte IO elements
                count = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
                offset += count * 10  # ID (2) + value (8)
                
                # Variable length IO elements
                count = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
                for _ in range(count):
                    offset += 2  # ID
                    length = struct.unpack('>H', data[offset:offset + 2])[0]
                    offset += 2
                    offset += length
                    
        except Exception:
            pass
        
        return offset
