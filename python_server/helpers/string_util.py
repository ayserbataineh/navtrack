"""String utilities."""

from typing import Optional


class StringUtil:
    """Utility class for string operations."""
    
    @staticmethod
    def convert_string_to_bytes(data: str) -> bytes:
        """Convert string to bytes."""
        return data.encode('ascii', errors='replace')
    
    @staticmethod
    def convert_bytes_to_string(data: bytes) -> str:
        """Convert bytes to ASCII string."""
        return data.decode('ascii', errors='replace')
    
    @staticmethod
    def is_digits_only(value: str) -> bool:
        """Check if string contains only digits."""
        return value.isdigit()
    
    @staticmethod
    def get_safe(array: list, index: int, default: Optional[str] = None) -> Optional[str]:
        """Safely get element from array."""
        try:
            if 0 <= index < len(array):
                return array[index]
        except (TypeError, IndexError):
            pass
        return default
    
    @staticmethod
    def parse_int(value: str, default: int = 0) -> int:
        """Safely parse string to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def parse_float(value: str, default: float = 0.0) -> float:
        """Safely parse string to float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
