"""Message reader for string-based GPS messages."""

from typing import Optional


class MessageReader:
    """Reader for string-based message parsing."""
    
    def __init__(self, message: str):
        self._message = message
        self.index = 0
    
    def get(self, length: int) -> str:
        """Get specified number of characters."""
        result = self._message[self.index:self.index + length]
        self.index += length
        return result
    
    def skip(self, count: int) -> 'MessageReader':
        """Skip specified number of characters."""
        self.index += count
        return self
    
    def get_until(self, char: str, extra: Optional[int] = None) -> str:
        """Get characters until specified character is found."""
        remaining = self._message[self.index:]
        pos = remaining.find(char)
        
        if pos == -1:
            raise ValueError(f"Character '{char}' not found")
        
        if extra:
            pos += extra
        
        result = remaining[:pos]
        self.index += pos + 1
        return result
    
    def reset(self) -> None:
        """Reset reader position."""
        self.index = 0
    
    @property
    def remaining(self) -> str:
        """Get remaining string."""
        return self._message[self.index:]
    
    @property
    def length(self) -> int:
        """Get total message length."""
        return len(self._message)
