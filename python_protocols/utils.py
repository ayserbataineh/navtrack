"""
Utility Functions for GPS Protocol Parsing

This module provides common utility functions used across protocol handlers
for parsing GPS tracking data.
"""

from datetime import datetime
from typing import Optional, Tuple
import struct


def hex_to_bytes(hex_string: str) -> bytes:
    """
    Convert a hex string to bytes.
    
    Args:
        hex_string: Hex string (with or without spaces)
        
    Returns:
        Bytes representation
    """
    return bytes.fromhex(hex_string.replace(" ", ""))


def bytes_to_hex(data: bytes) -> str:
    """
    Convert bytes to a hex string.
    
    Args:
        data: Byte data
        
    Returns:
        Hex string representation
    """
    return data.hex().upper()


def bytes_to_int(data: bytes, little_endian: bool = False) -> int:
    """
    Convert bytes to integer.
    
    Args:
        data: Byte data
        little_endian: If True, use little endian byte order
        
    Returns:
        Integer value
    """
    return int.from_bytes(data, byteorder='little' if little_endian else 'big')


def bytes_to_signed_int(data: bytes, little_endian: bool = False) -> int:
    """
    Convert bytes to signed integer.
    
    Args:
        data: Byte data
        little_endian: If True, use little endian byte order
        
    Returns:
        Signed integer value
    """
    return int.from_bytes(data, byteorder='little' if little_endian else 'big', signed=True)


def convert_dmm_lat_to_decimal(value: str, direction: str) -> float:
    """
    Convert latitude from DMM (Degrees Minutes.Minutes) to decimal degrees.
    
    Args:
        value: Latitude value in DMM format (e.g., "2234.4669")
        direction: Direction 'N' or 'S'
        
    Returns:
        Latitude in decimal degrees
    """
    try:
        degrees = int(value[:2])
        minutes = float(value[2:])
        decimal = degrees + (minutes / 60)
        if direction.upper() == 'S':
            decimal = -decimal
        return decimal
    except (ValueError, IndexError):
        return 0.0


def convert_dmm_long_to_decimal(value: str, direction: str) -> float:
    """
    Convert longitude from DMM (Degrees Minutes.Minutes) to decimal degrees.
    
    Args:
        value: Longitude value in DMM format (e.g., "11354.3287")
        direction: Direction 'E' or 'W'
        
    Returns:
        Longitude in decimal degrees
    """
    try:
        degrees = int(value[:3])
        minutes = float(value[3:])
        decimal = degrees + (minutes / 60)
        if direction.upper() == 'W':
            decimal = -decimal
        return decimal
    except (ValueError, IndexError):
        return 0.0


def knots_to_kph(knots: float) -> float:
    """
    Convert speed from knots to kilometers per hour.
    
    Args:
        knots: Speed in knots
        
    Returns:
        Speed in km/h
    """
    return knots * 1.852


def kph_to_knots(kph: float) -> float:
    """
    Convert speed from kilometers per hour to knots.
    
    Args:
        kph: Speed in km/h
        
    Returns:
        Speed in knots
    """
    return kph / 1.852


def parse_date_yymmdd(value: str) -> Optional[datetime]:
    """
    Parse date from YYMMDD format.
    
    Args:
        value: Date string in YYMMDD format
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        year = int(value[0:2]) + 2000
        month = int(value[2:4])
        day = int(value[4:6])
        return datetime(year, month, day)
    except (ValueError, IndexError):
        return None


def parse_datetime_yymmddhhmmss(value: str) -> Optional[datetime]:
    """
    Parse datetime from YYMMDDHHMMSS format.
    
    Args:
        value: Datetime string in YYMMDDHHMMSS format
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        year = int(value[0:2]) + 2000
        month = int(value[2:4])
        day = int(value[4:6])
        hour = int(value[6:8])
        minute = int(value[8:10])
        second = int(value[10:12])
        return datetime(year, month, day, hour, minute, second)
    except (ValueError, IndexError):
        return None


def parse_datetime_yyyymmddhhmmss(value: str) -> Optional[datetime]:
    """
    Parse datetime from YYYYMMDDHHMMSS format.
    
    Args:
        value: Datetime string in YYYYMMDDHHMMSS format
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        year = int(value[0:4])
        month = int(value[4:6])
        day = int(value[6:8])
        hour = int(value[8:10])
        minute = int(value[10:12])
        second = int(value[12:14])
        return datetime(year, month, day, hour, minute, second)
    except (ValueError, IndexError):
        return None


def unix_timestamp_to_datetime(timestamp: int, milliseconds: bool = False) -> datetime:
    """
    Convert Unix timestamp to datetime.
    
    Args:
        timestamp: Unix timestamp (seconds or milliseconds)
        milliseconds: If True, timestamp is in milliseconds
        
    Returns:
        datetime object
    """
    if milliseconds:
        return datetime.utcfromtimestamp(timestamp / 1000)
    return datetime.utcfromtimestamp(timestamp)


def calculate_crc16(data: bytes, polynomial: int = 0xA001, initial: int = 0xFFFF) -> int:
    """
    Calculate CRC-16 checksum.
    
    Args:
        data: Byte data to checksum
        polynomial: CRC polynomial (default: Modbus)
        initial: Initial CRC value
        
    Returns:
        CRC-16 checksum value
    """
    crc = initial
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
    return crc


def calculate_crc8(data: bytes, polynomial: int = 0x31, initial: int = 0x00) -> int:
    """
    Calculate CRC-8 checksum.
    
    Args:
        data: Byte data to checksum
        polynomial: CRC polynomial
        initial: Initial CRC value
        
    Returns:
        CRC-8 checksum value
    """
    crc = initial
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


def calculate_xor_checksum(data: bytes) -> int:
    """
    Calculate XOR checksum.
    
    Args:
        data: Byte data to checksum
        
    Returns:
        XOR checksum value
    """
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum


class ByteReader:
    """
    Helper class for reading bytes from a buffer.
    
    This class provides convenient methods for reading different data types
    from a byte buffer, similar to the ByteReader in the C# implementation.
    """
    
    def __init__(self, data: bytes):
        """
        Initialize the ByteReader.
        
        Args:
            data: Byte buffer to read from
        """
        self._data = data
        self._position = 0
    
    @property
    def position(self) -> int:
        """Current read position."""
        return self._position
    
    @property
    def bytes_left(self) -> int:
        """Number of bytes remaining."""
        return len(self._data) - self._position
    
    def reset(self) -> None:
        """Reset position to start of buffer."""
        self._position = 0
    
    def skip(self, count: int) -> None:
        """Skip a number of bytes."""
        self._position += count
    
    def get_one(self) -> int:
        """Read a single byte."""
        value = self._data[self._position]
        self._position += 1
        return value
    
    def get(self, count: int) -> bytes:
        """Read a number of bytes."""
        value = self._data[self._position:self._position + count]
        self._position += count
        return value
    
    def get_until(self, terminator: int) -> bytes:
        """Read bytes until a terminator byte is found."""
        start = self._position
        while self._position < len(self._data) and self._data[self._position] != terminator:
            self._position += 1
        value = self._data[start:self._position]
        self._position += 1  # Skip terminator
        return value
    
    def get_short(self, little_endian: bool = False) -> int:
        """Read a 16-bit short."""
        data = self.get(2)
        return bytes_to_signed_int(data, little_endian)
    
    def get_ushort(self, little_endian: bool = False) -> int:
        """Read an unsigned 16-bit short."""
        data = self.get(2)
        return bytes_to_int(data, little_endian)
    
    def get_int(self, little_endian: bool = False) -> int:
        """Read a 32-bit integer."""
        data = self.get(4)
        return bytes_to_signed_int(data, little_endian)
    
    def get_uint(self, little_endian: bool = False) -> int:
        """Read an unsigned 32-bit integer."""
        data = self.get(4)
        return bytes_to_int(data, little_endian)
    
    def get_long(self, little_endian: bool = False) -> int:
        """Read a 64-bit long."""
        data = self.get(8)
        return bytes_to_signed_int(data, little_endian)
    
    def get_ulong(self, little_endian: bool = False) -> int:
        """Read an unsigned 64-bit long."""
        data = self.get(8)
        return bytes_to_int(data, little_endian)
    
    def get_string(self, length: int, encoding: str = 'ascii') -> str:
        """Read a string of specified length."""
        data = self.get(length)
        return data.decode(encoding)
    
    def get_string_until(self, terminator: int, encoding: str = 'ascii') -> str:
        """Read a null-terminated string."""
        data = self.get_until(terminator)
        return data.decode(encoding)


class MessageReader:
    """
    Helper class for reading string messages.
    
    This class provides methods for parsing text-based GPS messages.
    """
    
    def __init__(self, message: str):
        """
        Initialize the MessageReader.
        
        Args:
            message: String message to parse
        """
        self._message = message
        self._position = 0
    
    @property
    def position(self) -> int:
        """Current read position."""
        return self._position
    
    @property
    def remaining(self) -> str:
        """Remaining unparsed message."""
        return self._message[self._position:]
    
    def reset(self) -> None:
        """Reset position to start of message."""
        self._position = 0
    
    def skip(self, count: int) -> None:
        """Skip a number of characters."""
        self._position += count
    
    def get(self, count: int) -> str:
        """Read a number of characters."""
        value = self._message[self._position:self._position + count]
        self._position += count
        return value
    
    def get_until(self, delimiter: str) -> str:
        """Read until a delimiter is found."""
        index = self._message.find(delimiter, self._position)
        if index == -1:
            value = self._message[self._position:]
            self._position = len(self._message)
        else:
            value = self._message[self._position:index]
            self._position = index + len(delimiter)
        return value
    
    def get_int(self, count: int) -> Optional[int]:
        """Read an integer of specified digit count."""
        try:
            return int(self.get(count))
        except ValueError:
            return None
    
    def get_float(self, count: int) -> Optional[float]:
        """Read a float of specified character count."""
        try:
            return float(self.get(count))
        except ValueError:
            return None
    
    def split(self, delimiter: str) -> list:
        """Split the remaining message by delimiter."""
        return self._message.split(delimiter)
