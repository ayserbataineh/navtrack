"""Concox/JM-VL GPS protocol implementation (GT06, GT06N, WeTrack, etc.)."""

import struct
from typing import Optional, List
from datetime import datetime

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..models.enums import CardinalPoint
from ..helpers.gps_util import GpsUtil
from ..helpers.datetime_util import DateTimeUtil
from ..helpers.hex_util import HexUtil


# Protocol numbers for Concox/GT06
class ProtocolNumber:
    LOGIN = 0x01
    HEARTBEAT = 0x13
    LOCATION = 0x12
    LOCATION_NEW = 0x22
    ALARM = 0x16
    STATUS = 0x13


class ConcoxProtocol(BaseProtocol):
    """Concox GPS tracker protocol (GT06, GT06N, JM-VL, WeTrack, etc.)."""
    
    @property
    def port(self) -> int:
        return 7013
    
    @property
    def message_start(self) -> bytes:
        return b"\x78\x78"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\x0D\x0A"]


class ConcoxMessageHandler(BaseMessageHandler):
    """Message handler for Concox protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse Concox GPS message."""
        data = input_data.data_message.bytes
        
        # Check for extended packet (0x79 0x79)
        extended = len(data) >= 2 and data[0] == 0x79 and data[1] == 0x79
        offset = 1 if extended else 0
        
        # Get protocol number
        if len(data) < 4 + offset:
            return None
        
        protocol_num = data[3 + offset]
        
        if protocol_num == ProtocolNumber.LOGIN:
            return self._handle_login(input_data, data, offset)
        elif protocol_num == ProtocolNumber.HEARTBEAT:
            return self._handle_heartbeat(input_data, data, offset)
        elif protocol_num in (ProtocolNumber.LOCATION, ProtocolNumber.LOCATION_NEW):
            return self._parse_location(input_data, data, offset)
        
        return None
    
    def _handle_login(
        self, 
        input_data: MessageInput, 
        data: bytes, 
        offset: int
    ) -> Optional[DeviceMessage]:
        """Handle login message."""
        try:
            # IMEI is at position 4-12 (8 bytes, BCD encoded)
            start = 4 + offset
            imei_bytes = data[start:start + 8]
            imei = imei_bytes.hex()
            
            # Remove leading zeros
            if imei.startswith("0"):
                imei = imei[1:]
            
            input_data.connection_context.set_device(imei)
            
            # Send login response
            serial = data[-6:-4] if len(data) >= 6 else b"\x00\x01"
            response = self._build_response(ProtocolNumber.LOGIN, serial)
            input_data.write(response)
            
        except Exception:
            pass
        
        return None
    
    def _handle_heartbeat(
        self, 
        input_data: MessageInput, 
        data: bytes, 
        offset: int
    ) -> Optional[DeviceMessage]:
        """Handle heartbeat message."""
        try:
            serial = data[-6:-4] if len(data) >= 6 else b"\x00\x01"
            response = self._build_response(ProtocolNumber.HEARTBEAT, serial)
            input_data.write(response)
        except Exception:
            pass
        
        return None
    
    def _parse_location(
        self, 
        input_data: MessageInput, 
        data: bytes, 
        offset: int
    ) -> Optional[DeviceMessage]:
        """Parse location message."""
        try:
            # Date/Time (6 bytes at position 4)
            base = 4 + offset
            hex_data = HexUtil.convert_bytes_to_hex_array(data)
            
            msg_date = DateTimeUtil.new_from_hex(
                hex_data[base],      # year
                hex_data[base + 1],  # month
                hex_data[base + 2],  # day
                hex_data[base + 3],  # hour
                hex_data[base + 4],  # minute
                hex_data[base + 5]   # second
            )
            
            # Satellites (lower nibble of byte at base + 6)
            satellites = int(hex_data[base + 6][1], 16)
            
            # Latitude (4 bytes at base + 7, BCD * 30000 * 60)
            lat_bytes = data[base + 7:base + 11]
            lat_raw = struct.unpack('>I', lat_bytes)[0]
            lat_degrees = int(lat_raw / 30000 / 60)
            lat_minutes = lat_raw / 30000 - lat_degrees * 60
            
            # Longitude (4 bytes at base + 11)
            lon_bytes = data[base + 11:base + 15]
            lon_raw = struct.unpack('>I', lon_bytes)[0]
            lon_degrees = int(lon_raw / 30000 / 60)
            lon_minutes = lon_raw / 30000 - lon_degrees * 60
            
            # Speed (1 byte at base + 15)
            speed = data[base + 15]
            
            # Course and status (2 bytes at base + 16)
            course_status = (data[base + 16] << 8) | data[base + 17]
            
            # Parse course/status bits
            course_str = bin(course_status)[2:].zfill(16)
            lon_west = course_str[4] == '1'
            lat_south = course_str[5] == '0'
            valid = course_str[3] == '1'
            heading = int(course_str[6:], 2)
            
            # Determine cardinal points
            lat_cardinal = CardinalPoint.SOUTH if lat_south else CardinalPoint.NORTH
            lon_cardinal = CardinalPoint.WEST if lon_west else CardinalPoint.EAST
            
            latitude = GpsUtil.convert_dmm_to_decimal_with_cardinal(
                lat_degrees, lat_minutes, lat_cardinal
            )
            longitude = GpsUtil.convert_dmm_to_decimal_with_cardinal(
                lon_degrees, lon_minutes, lon_cardinal
            )
            
            # GSM info (if available)
            gsm_mcc = None
            gsm_mnc = None
            gsm_lac = None
            gsm_cell_id = None
            
            try:
                gsm_base = base + 18
                mcc_bytes = data[gsm_base:gsm_base + 2]
                gsm_mcc = str(struct.unpack('>H', mcc_bytes)[0])
                gsm_mnc = str(data[gsm_base + 2])
                lac_bytes = data[gsm_base + 3:gsm_base + 5]
                gsm_lac = str(struct.unpack('>H', lac_bytes)[0])
                cell_bytes = data[gsm_base + 5:gsm_base + 8]
                gsm_cell_id = struct.unpack('>I', b'\x00' + cell_bytes)[0]
            except Exception:
                pass
            
            return DeviceMessage(
                date=msg_date,
                satellites=satellites,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                valid=valid,
                heading=heading,
                gsm_mobile_country_code=gsm_mcc,
                gsm_mobile_network_code=gsm_mnc,
                gsm_location_area_code=gsm_lac,
                gsm_cell_id=gsm_cell_id
            )
            
        except Exception:
            return None
    
    def _build_response(self, protocol_num: int, serial: bytes) -> bytes:
        """Build protocol response message."""
        # Response: 78 78 05 [protocol] [serial] [crc] 0D 0A
        content = bytes([0x05, protocol_num]) + serial
        crc = self._calculate_crc(content)
        return b"\x78\x78" + content + crc + b"\x0D\x0A"
    
    def _calculate_crc(self, data: bytes) -> bytes:
        """Calculate CRC16 for Concox protocol."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0x8408
                else:
                    crc >>= 1
        return struct.pack('>H', crc)


# GT06 is the same as Concox
GT06Protocol = ConcoxProtocol
GT06MessageHandler = ConcoxMessageHandler
