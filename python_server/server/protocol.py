"""Base protocol definition."""

from abc import ABC
from typing import List, Optional


class BaseProtocol(ABC):
    """Base class for GPS device protocols."""
    
    @property
    def port(self) -> int:
        """TCP port for this protocol."""
        raise NotImplementedError("Protocol must define a port")
    
    @property
    def name(self) -> str:
        """Protocol name."""
        return self.__class__.__name__.replace("Protocol", "")
    
    @property
    def message_start(self) -> bytes:
        """Message start bytes (optional)."""
        return b""
    
    @property
    def message_end(self) -> List[bytes]:
        """Message end bytes (optional)."""
        return [b""]
    
    @property
    def split_message_by(self) -> str:
        """Delimiter to split message by."""
        return ""
    
    def get_message_length(self, buffer: bytes, bytes_read: int) -> Optional[int]:
        """
        Get expected message length from buffer.
        
        Override this for protocols with length-prefixed messages.
        Return None if message length cannot be determined.
        """
        return None
    
    def __str__(self) -> str:
        return f"{self.name}Protocol"
    
    def __repr__(self) -> str:
        return f"<{self.name}Protocol port={self.port}>"
