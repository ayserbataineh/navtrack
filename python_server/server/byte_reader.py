"""Byte reader for binary GPS messages."""

from typing import List, Optional, TypeVar
import struct

T = TypeVar('T')


class ByteReader:
    """Reader for binary data with position tracking."""
    
    def __init__(self, data: bytes, hex_array: List[str]):
        self._data = data
        self._hex = hex_array
        self.index = 0
    
    @property
    def bytes_left(self) -> int:
        """Get remaining bytes to read."""
        return len(self._data) - self.index
    
    def get_one(self) -> int:
        """Get a single byte as int."""
        if self.index >= len(self._data):
            raise IndexError("No more bytes to read")
        value = self._data[self.index]
        self.index += 1
        return value
    
    def get_byte(self) -> int:
        """Get a single byte."""
        return self.get_one()
    
    def get(self, length: int, count: bool = True, reverse: bool = False) -> bytes:
        """Get specified number of bytes."""
        if self.index + length > len(self._data):
            raise IndexError(f"Not enough bytes: need {length}, have {self.bytes_left}")
        
        data = self._data[self.index:self.index + length]
        
        if count:
            self.index += length
        
        if reverse:
            data = bytes(reversed(data))
        
        return data
    
    def get_short(self) -> int:
        """Get signed 16-bit integer (big-endian)."""
        data = self.get(2, reverse=True)
        return struct.unpack('>h', bytes(reversed(data)))[0]
    
    def get_ushort(self) -> int:
        """Get unsigned 16-bit integer (big-endian)."""
        data = self.get(2, reverse=True)
        return struct.unpack('>H', bytes(reversed(data)))[0]
    
    def get_int(self) -> int:
        """Get signed 32-bit integer (little-endian)."""
        data = self.get(4)
        return struct.unpack('<i', data)[0]
    
    def get_uint(self) -> int:
        """Get unsigned 32-bit integer (little-endian)."""
        data = self.get(4)
        return struct.unpack('<I', data)[0]
    
    def get_int_be(self) -> int:
        """Get signed 32-bit integer (big-endian)."""
        data = self.get(4)
        return struct.unpack('>i', data)[0]
    
    def get_uint_be(self) -> int:
        """Get unsigned 32-bit integer (big-endian)."""
        data = self.get(4)
        return struct.unpack('>I', data)[0]
    
    def get_short_be(self) -> int:
        """Get signed 16-bit integer (big-endian)."""
        data = self.get(2)
        return struct.unpack('>h', data)[0]
    
    def get_ushort_be(self) -> int:
        """Get unsigned 16-bit integer (big-endian)."""
        data = self.get(2)
        return struct.unpack('>H', data)[0]
    
    def get_long(self) -> int:
        """Get signed 64-bit integer (little-endian)."""
        data = self.get(8)
        return struct.unpack('<q', data)[0]
    
    def get_ulong(self) -> int:
        """Get unsigned 64-bit integer (little-endian)."""
        data = self.get(8)
        return struct.unpack('<Q', data)[0]
    
    def get_long_be(self) -> int:
        """Get signed 64-bit integer (big-endian)."""
        data = self.get(8)
        return struct.unpack('>q', data)[0]
    
    def get_ulong_be(self) -> int:
        """Get unsigned 64-bit integer (big-endian)."""
        data = self.get(8)
        return struct.unpack('>Q', data)[0]
    
    def get_float(self) -> float:
        """Get 32-bit float (little-endian)."""
        data = self.get(4)
        return struct.unpack('<f', data)[0]
    
    def get_double(self) -> float:
        """Get 64-bit float (little-endian)."""
        data = self.get(8)
        return struct.unpack('<d', data)[0]
    
    def get_medium_int_le(self) -> int:
        """Get 24-bit integer (little-endian)."""
        data = self.get(3)
        return struct.unpack('<i', data + b'\x00')[0]
    
    def skip(self, count: int) -> 'ByteReader':
        """Skip specified number of bytes."""
        if count > 0:
            self.index += count
        return self
    
    def get_until(self, byte: int, extra: Optional[int] = None) -> bytes:
        """Get bytes until specified byte is found."""
        try:
            remaining = self._data[self.index:]
            pos = remaining.index(bytes([byte]))
            if extra:
                pos += extra
            result = self._data[self.index:self.index + pos]
            self.index += pos + 1
            return result
        except ValueError:
            raise IndexError(f"Byte {byte:02X} not found in remaining data")
    
    def get_hex_array(self, length: int) -> List[str]:
        """Get hex string array."""
        end_index = self.index + length
        result = self._hex[self.index:end_index]
        self.index = end_index
        return result
    
    def get_hex_string(self, length: int) -> str:
        """Get hex string."""
        return "".join(self.get_hex_array(length))
    
    def reset(self) -> None:
        """Reset reader position."""
        self.index = 0
    
    def peek(self, length: int = 1) -> bytes:
        """Peek at bytes without advancing position."""
        return self._data[self.index:self.index + length]
