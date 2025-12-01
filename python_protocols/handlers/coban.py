"""
Coban Protocol Message Handler

This module implements the message handler for Coban GPS103/GPS303 trackers.

Protocol Specification:
- Text-based protocol
- TCP communication
- Messages end with semicolon (;)

Message Types:
1. Authentication: ##,imei:XXXXXXXXXXXXXXX,A;
2. Heartbeat: XXXXXXXXXXXXXXX (IMEI only)
3. Location: imei:XXXXXXXXXXXXXXX,tracker,YYMMDDHHMMSS,...

Location Message Format:
imei:XXXXXXXXXXXXXXX,tracker,YYMMDDHHMMSS,phone,F/L,HHMMSS.SSS,A/V,DDMM.MMMM,N/S,DDDMM.MMMM,E/W,speed,heading,altitude;

Where:
- F/L: Full/Low GPS signal
- A/V: Active/Void (valid/invalid GPS fix)
- N/S: North/South
- E/W: East/West
"""

import re
from datetime import datetime
from typing import List, Optional
from ..device_message import DeviceMessage
from ..utils import convert_dmm_lat_to_decimal, convert_dmm_long_to_decimal, knots_to_kph
from .base import BaseMessageHandler


class CobanMessageHandler(BaseMessageHandler):
    """
    Message handler for Coban GPS103/GPS303 trackers.
    
    Supports:
    - GPS103, GPS103A, GPS103B
    - GPS303, GPS303D, GPS303F
    - TK103, TK303
    - Other Coban-compatible devices
    
    Protocol features:
    - Text-based message format
    - Authentication via IMEI
    - Heartbeat messages
    - Location tracking
    """
    
    # Regex patterns
    AUTH_PATTERN = re.compile(r'##,imei:(\d+),A;')
    LOCATION_PATTERN = re.compile(
        r'imei:(\d+),'  # IMEI
        r'([^,]*),'     # Message type (tracker, etc.)
        r'(\d+)?,'      # Date time (YYMMDDHHMMSS)
        r'([^,]*),'     # Phone number
        r'([FL]),'      # GPS signal (Full/Low)
        r'(\d+\.?\d*)?,' # GPS time (HHMMSS.SSS)
        r'([AV]),'      # Valid flag (Active/Void)
        r'(\d+\.?\d*),' # Latitude (DDMM.MMMM)
        r'([NS]),'      # N/S
        r'(\d+\.?\d*),' # Longitude (DDDMM.MMMM)
        r'([EW]),'      # E/W
        r'(\d+\.?\d*),' # Speed (knots)
        r'(\d*\.?\d*)?,?' # Heading
        r'(\d*)?' # Altitude
    )
    
    def __init__(self):
        super().__init__()
        self._pending_auth_response: Optional[bytes] = None
        self._pending_heartbeat_response: Optional[bytes] = None
    
    def parse_range(self, data: bytes) -> List[DeviceMessage]:
        """
        Parse Coban message data.
        
        Args:
            data: Raw byte data from the device
            
        Returns:
            List of parsed DeviceMessage objects
        """
        try:
            message_str = data.decode('ascii').strip()
        except UnicodeDecodeError:
            return []
        
        # Try authentication message
        auth_result = self._parse_authentication(message_str)
        if auth_result is not None:
            return auth_result
        
        # Try heartbeat message
        heartbeat_result = self._parse_heartbeat(message_str)
        if heartbeat_result is not None:
            return heartbeat_result
        
        # Try location message
        return self._parse_location(message_str)
    
    def _parse_authentication(self, message: str) -> Optional[List[DeviceMessage]]:
        """Parse authentication message (##,imei:XXX,A;)."""
        match = self.AUTH_PATTERN.match(message)
        if match:
            imei = match.group(1)
            if imei.isdigit():
                self.set_device_id(imei)
                self._pending_auth_response = b'LOAD'
            return []
        return None
    
    def _parse_heartbeat(self, message: str) -> Optional[List[DeviceMessage]]:
        """Parse heartbeat message (IMEI only)."""
        if message.isdigit() and len(message) == 15:
            self._pending_heartbeat_response = b'ON'
            return []
        return None
    
    def _parse_location(self, message: str) -> List[DeviceMessage]:
        """Parse location message."""
        match = self.LOCATION_PATTERN.match(message)
        if not match:
            return []
        
        groups = match.groups()
        
        # Set device ID if not already set
        imei = groups[0]
        if not self.is_authenticated():
            self.set_device_id(imei)
        
        device_message = DeviceMessage()
        
        # Parse date/time
        date_str = groups[2]
        if date_str and len(date_str) >= 10:
            device_message.date = self._parse_datetime(date_str)
        
        # GPS valid flag
        device_message.valid = groups[6] == 'A'
        
        # Parse coordinates
        try:
            lat_str = groups[7]
            lat_dir = groups[8]
            lon_str = groups[9]
            lon_dir = groups[10]
            
            device_message.latitude = convert_dmm_lat_to_decimal(lat_str, lat_dir)
            device_message.longitude = convert_dmm_long_to_decimal(lon_str, lon_dir)
        except (ValueError, IndexError):
            pass
        
        # Parse speed (convert from knots to km/h)
        try:
            speed_knots = float(groups[11])
            device_message.speed = int(knots_to_kph(speed_knots))
        except (ValueError, TypeError):
            pass
        
        # Parse heading
        try:
            heading_str = groups[12]
            if heading_str and heading_str not in ('', '1'):
                device_message.heading = int(float(heading_str))
        except (ValueError, TypeError):
            pass
        
        # Parse altitude
        try:
            alt_str = groups[13]
            if alt_str:
                device_message.altitude = int(alt_str)
        except (ValueError, TypeError):
            pass
        
        return [device_message]
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse date from DDMMYYHHMMSS or YYMMDDHHMMSS format."""
        try:
            if len(date_str) >= 12:
                # Assuming DDMMYYHHMMSS format
                day = int(date_str[0:2])
                month = int(date_str[2:4])
                year = int(date_str[4:6]) + 2000
                hour = int(date_str[6:8])
                minute = int(date_str[8:10])
                second = 0
                if len(date_str) >= 12:
                    second = int(date_str[10:12])
                return datetime(year, month, day, hour, minute, second)
            elif len(date_str) >= 10:
                # Shorter format
                day = int(date_str[0:2])
                month = int(date_str[2:4])
                year = int(date_str[4:6]) + 2000
                hour = int(date_str[6:8])
                minute = int(date_str[8:10])
                return datetime(year, month, day, hour, minute, 0)
        except (ValueError, IndexError):
            pass
        return None
    
    def get_response(self, data: bytes) -> Optional[bytes]:
        """
        Generate response for Coban device.
        
        Returns 'LOAD' for authentication, 'ON' for heartbeat.
        """
        if self._pending_auth_response:
            response = self._pending_auth_response
            self._pending_auth_response = None
            return response
        
        if self._pending_heartbeat_response:
            response = self._pending_heartbeat_response
            self._pending_heartbeat_response = None
            return response
        
        return None
