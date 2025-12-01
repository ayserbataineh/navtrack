"""Coban GPS protocol implementation."""

import re
from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gps_util import GpsUtil
from ..helpers.speed_util import SpeedUtil
from ..helpers.string_util import StringUtil
from ..helpers.datetime_util import DateTimeUtil


class CobanProtocol(BaseProtocol):
    """Coban GPS tracker protocol (GPS102, GPS103, GPS106, TK102, TK103, etc.)."""
    
    @property
    def port(self) -> int:
        return 7007
    
    @property
    def message_end(self) -> List[bytes]:
        return [b";"]


class CobanMessageHandler(BaseMessageHandler):
    """Message handler for Coban protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Coban GPS message."""
        return self.parse_with_handlers(
            input_data,
            self._parse_authentication,
            self._parse_heartbeat,
            self._parse_location
        )
    
    def _parse_authentication(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Handle device authentication (##,imei:XXXXX,A;)."""
        match = re.match(r"##,imei:(\d+),A;", input_data.data_message.string)
        
        if match:
            imei = match.group(1)
            if StringUtil.is_digits_only(imei):
                input_data.connection_context.set_device(imei)
                input_data.write(b"LOAD")
        
        return None
    
    def _parse_heartbeat(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Handle heartbeat messages (just digits)."""
        msg = input_data.data_message.string.strip().rstrip(';')
        
        if StringUtil.is_digits_only(msg):
            input_data.write(b"ON")
        
        return None
    
    def _parse_location(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """
        Parse location message.
        
        Format: imei:XXXXX,tracker,DDMMYYHHMMSS,phone,F,HHMMSS.SSS,A,DDMM.MMMM,N,DDDMM.MMMM,E,speed,heading,altitude;
        """
        parts = input_data.data_message.comma_split
        
        if len(parts) < 12:
            return None
        
        # Extract IMEI
        imei = parts[0].replace("imei:", "")
        input_data.connection_context.set_device(imei)
        
        # Parse date from field 2 (DDMMYYHHMMSS format or YYMMDD format)
        date_str = parts[2]
        
        try:
            if len(date_str) >= 10:
                # YYMMDDHHMMSS format or similar
                reader = _MessageReader(date_str)
                day = reader.get(2)
                month = reader.get(2)
                year = reader.get(2)
                hour = reader.get(2)
                minute = reader.get(2)
                
                msg_date = DateTimeUtil.new(year, month, day, hour, minute, "0")
            else:
                msg_date = None
        except Exception:
            msg_date = None
        
        # Check GPS validity (field 4)
        valid = parts[4] == "F" if len(parts) > 4 else None
        
        # Parse coordinates
        try:
            latitude = GpsUtil.convert_dmm_lat_to_decimal(parts[7], parts[8])
            longitude = GpsUtil.convert_dmm_long_to_decimal(parts[9], parts[10])
        except (IndexError, ValueError):
            return None
        
        # Parse speed
        try:
            speed = SpeedUtil.knots_to_kph(float(parts[11]))
        except (IndexError, ValueError):
            speed = None
        
        # Parse heading
        try:
            heading_str = parts[12] if len(parts) > 12 else None
            heading = int(float(heading_str)) if heading_str and heading_str != "1" else None
        except (ValueError, TypeError):
            heading = None
        
        # Parse altitude
        try:
            altitude = int(float(parts[13])) if len(parts) > 13 else None
        except (ValueError, IndexError):
            altitude = None
        
        return DeviceMessage(
            date=msg_date,
            valid=valid,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            altitude=altitude
        )


class _MessageReader:
    """Simple string reader for parsing."""
    
    def __init__(self, message: str):
        self._message = message
        self._index = 0
    
    def get(self, length: int) -> str:
        result = self._message[self._index:self._index + length]
        self._index += length
        return result
