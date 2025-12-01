"""Hex string utilities."""

from typing import List, Union


class HexUtil:
    """Utility class for hex string operations."""
    
    @staticmethod
    def convert_bytes_to_hex_array(data: bytes) -> List[str]:
        """Convert bytes to list of hex strings."""
        return [f"{b:02X}" for b in data]
    
    @staticmethod
    def convert_hex_array_to_string(hex_array: List[str]) -> str:
        """Convert list of hex strings to single hex string."""
        return "".join(hex_array)
    
    @staticmethod
    def convert_hex_string_to_bytes(hex_string: str) -> bytes:
        """Convert hex string to bytes."""
        # Remove spaces if present
        hex_string = hex_string.replace(" ", "")
        return bytes.fromhex(hex_string)
    
    @staticmethod
    def convert_hex_string_to_array(hex_string: str) -> List[str]:
        """Convert hex string to list of hex byte strings."""
        hex_string = hex_string.replace(" ", "")
        return [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    
    @staticmethod
    def convert_hex_array_to_bytes(hex_array: List[str]) -> bytes:
        """Convert list of hex strings to bytes."""
        return bytes(int(h, 16) for h in hex_array)
    
    @staticmethod
    def convert_string_to_hex(data: str) -> str:
        """Convert string to hex string."""
        return data.encode().hex().upper()
