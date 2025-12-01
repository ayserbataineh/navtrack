"""Data message wrapper for GPS messages."""

from typing import List, Optional

from .byte_reader import ByteReader
from .message_reader import MessageReader
from ..helpers.hex_util import HexUtil


class DataMessage:
    """Wrapper for incoming GPS device messages."""
    
    def __init__(self, data: bytes, split_by: str = ""):
        self.bytes = data
        self.hex = HexUtil.convert_bytes_to_hex_array(data)
        self.hex_string = HexUtil.convert_hex_array_to_string(self.hex)
        
        # Try to decode as ASCII, replacing invalid chars
        self.string = data.decode('ascii', errors='replace')
        
        # Common splits
        self.comma_split = self.string.split(",")
        self.bar_split = self.string.split("|")
        
        # Custom split
        if split_by:
            self.split = self.string.split(split_by)
        else:
            self.split = self.comma_split
        
        # Readers
        self.reader = MessageReader(self.string)
        self.byte_reader = ByteReader(data, self.hex)
    
    def get_comma(self, index: int, default: str = "") -> str:
        """Get element from comma split."""
        if 0 <= index < len(self.comma_split):
            return self.comma_split[index]
        return default
    
    def get_bar(self, index: int, default: str = "") -> str:
        """Get element from bar split."""
        if 0 <= index < len(self.bar_split):
            return self.bar_split[index]
        return default
    
    def get_int(self, index: int, default: int = 0) -> int:
        """Get integer from comma split."""
        try:
            return int(self.comma_split[index])
        except (IndexError, ValueError):
            return default
    
    def get_float(self, index: int, default: float = 0.0) -> float:
        """Get float from comma split."""
        try:
            return float(self.comma_split[index])
        except (IndexError, ValueError):
            return default
