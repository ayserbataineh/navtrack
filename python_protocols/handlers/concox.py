"""
Concox Protocol Message Handler

This module implements the message handler for Concox GT06/GT06N trackers.

Protocol Specification:
- Binary protocol
- TCP communication
- Message start: 0x78 0x78 (or 0x79 0x79 for extended)
- Message end: 0x0D 0x0A

Message Structure:
- 2 bytes: Start bits (0x78 0x78)
- 1 byte: Packet length
- 1 byte: Protocol number
- N bytes: Information content
- 2 bytes: Information serial number
- 2 bytes: Error check (CRC-16 ITU)
- 2 bytes: Stop bits (0x0D 0x0A)

Protocol Numbers:
- 0x01: Login message
- 0x12: Location data (GPS)
- 0x13: Status message
- 0x15: String information
- 0x16: Alarm data
- 0x17: GPS LBS combined
- 0x22: Location data (GPS LBS status)
- 0x23: Heartbeat
"""

from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Tuple
from ..device_message import DeviceMessage
from ..utils import ByteReader, calculate_crc16
from .base import BaseMessageHandler


class ConcoxProtocolNumber(IntEnum):
    """Concox protocol message types."""
    LOGIN = 0x01
    HEARTBEAT = 0x13
    GPS_LOCATION = 0x22
    ALARM = 0x26
    GPS_LBS_STATUS = 0x32


class ConcoxMessageHandler(BaseMessageHandler):
    """
    Message handler for Concox GT06/GT06N trackers.
    
    Supports:
    - GT06, GT06N
    - JM01, JM08
    - GK309
    - Other Concox-compatible devices
    
    Protocol features:
    - Binary message format
    - CRC-16 verification
    - Login/Heartbeat acknowledgment
    - GPS + LBS data
    - Alarm events
    """
    
    # Standard message start bytes
    START_STANDARD = bytes([0x78, 0x78])
    START_EXTENDED = bytes([0x79, 0x79])
    STOP_BITS = bytes([0x0D, 0x0A])
    
    def __init__(self):
        super().__init__()
        self._serial_number: int = 0
        self._pending_response: Optional[bytes] = None
    
    def parse_range(self, data: bytes) -> List[DeviceMessage]:
        """
        Parse Concox message data.
        
        Args:
            data: Raw byte data from the device
            
        Returns:
            List of parsed DeviceMessage objects
        """
        # Check for valid message start
        if not data.startswith(self.START_STANDARD) and not data.startswith(self.START_EXTENDED):
            return []
        
        is_extended = data.startswith(self.START_EXTENDED)
        reader = ByteReader(data)
        
        # Skip start bits
        reader.skip(2)
        
        # Packet length
        if is_extended:
            packet_length = reader.get_ushort()
        else:
            packet_length = reader.get_one()
        
        # Protocol number
        protocol_number = reader.get_one()
        
        # Parse based on protocol number
        if protocol_number == ConcoxProtocolNumber.LOGIN:
            return self._parse_login(reader)
        elif protocol_number == ConcoxProtocolNumber.HEARTBEAT:
            return self._parse_heartbeat(reader)
        elif protocol_number in (ConcoxProtocolNumber.GPS_LOCATION, ConcoxProtocolNumber.GPS_LBS_STATUS):
            return self._parse_location(reader)
        elif protocol_number == ConcoxProtocolNumber.ALARM:
            return self._parse_alarm(reader)
        
        return []
    
    def _parse_login(self, reader: ByteReader) -> List[DeviceMessage]:
        """Parse login message and extract IMEI."""
        # IMEI is 8 bytes BCD encoded
        imei_bytes = reader.get(8)
        imei = self._decode_bcd(imei_bytes)
        
        if len(imei) >= 15:
            self.set_device_id(imei[:15])
        
        # Read serial number for response
        reader.skip(reader.bytes_left - 6)  # Skip to serial number
        self._serial_number = reader.get_ushort()
        
        # Create login response
        self._pending_response = self._create_response(ConcoxProtocolNumber.LOGIN, self._serial_number)
        
        return []
    
    def _parse_heartbeat(self, reader: ByteReader) -> List[DeviceMessage]:
        """Parse heartbeat message."""
        # Skip to serial number
        reader.skip(reader.bytes_left - 6)
        self._serial_number = reader.get_ushort()
        
        # Create heartbeat response
        self._pending_response = self._create_response(ConcoxProtocolNumber.HEARTBEAT, self._serial_number)
        
        return []
    
    def _parse_location(self, reader: ByteReader) -> List[DeviceMessage]:
        """Parse GPS location message."""
        message = DeviceMessage()
        
        # Date/Time (6 bytes: YY MM DD HH MM SS)
        year = 2000 + reader.get_one()
        month = reader.get_one()
        day = reader.get_one()
        hour = reader.get_one()
        minute = reader.get_one()
        second = reader.get_one()
        
        try:
            message.date = datetime(year, month, day, hour, minute, second)
        except ValueError:
            pass
        
        # GPS information length and satellites
        gps_info = reader.get_one()
        message.satellites = gps_info & 0x0F
        gps_length = (gps_info >> 4) & 0x0F
        
        # Latitude (4 bytes, unit: 1/30000 minutes)
        lat_raw = reader.get_uint()
        message.latitude = lat_raw / 30000.0 / 60.0
        
        # Longitude (4 bytes, unit: 1/30000 minutes)
        lon_raw = reader.get_uint()
        message.longitude = lon_raw / 30000.0 / 60.0
        
        # Speed (1 byte)
        message.speed = reader.get_one()
        
        # Course and status (2 bytes)
        course_status = reader.get_ushort()
        message.heading = course_status & 0x03FF
        
        # Extract status flags
        is_real_time = (course_status >> 13) & 0x01
        is_positioned = (course_status >> 12) & 0x01
        is_east = (course_status >> 11) & 0x01
        is_north = (course_status >> 10) & 0x01
        
        message.valid = is_positioned == 1
        
        if not is_east:
            message.longitude = -message.longitude
        if not is_north:
            message.latitude = -message.latitude
        
        return [message]
    
    def _parse_alarm(self, reader: ByteReader) -> List[DeviceMessage]:
        """Parse alarm message (similar to location but with alarm data)."""
        messages = self._parse_location(reader)
        
        if messages:
            # Mark as alarm
            messages[0].message_priority = "High"
            messages[0].additional_data["alarm"] = "true"
        
        return messages
    
    def _decode_bcd(self, data: bytes) -> str:
        """Decode BCD (Binary Coded Decimal) to string."""
        result = []
        for byte in data:
            high = (byte >> 4) & 0x0F
            low = byte & 0x0F
            if high <= 9:
                result.append(str(high))
            if low <= 9:
                result.append(str(low))
        return ''.join(result)
    
    def _create_response(self, protocol_number: int, serial_number: int) -> bytes:
        """Create a response message for the device."""
        # Response format:
        # 0x78 0x78 - start
        # 0x05 - length
        # protocol_number
        # serial_number (2 bytes)
        # CRC (2 bytes)
        # 0x0D 0x0A - end
        
        content = bytes([protocol_number]) + serial_number.to_bytes(2, byteorder='big')
        crc = self._calculate_crc(content)
        
        response = (
            self.START_STANDARD +
            bytes([len(content) + 4]) +  # Length includes CRC and serial
            content +
            crc.to_bytes(2, byteorder='big') +
            self.STOP_BITS
        )
        
        return response
    
    def _calculate_crc(self, data: bytes) -> int:
        """Calculate CRC-16 ITU for Concox protocol."""
        crc = 0xFFFF
        polynomial = 0x8408
        
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ polynomial
                else:
                    crc >>= 1
        
        return crc ^ 0xFFFF
    
    def get_response(self, data: bytes) -> Optional[bytes]:
        """
        Generate response for Concox device.
        
        Returns acknowledgment for login/heartbeat messages.
        """
        if self._pending_response:
            response = self._pending_response
            self._pending_response = None
            return response
        return None
