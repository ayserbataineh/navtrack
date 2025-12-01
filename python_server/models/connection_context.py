"""Connection context for GPS tracking server."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4

from .device import Device

if TYPE_CHECKING:
    from ..server.protocol import BaseProtocol


@dataclass
class ConnectionContext:
    """Represents a client connection context."""
    
    protocol: 'BaseProtocol'
    connection_id: UUID = field(default_factory=uuid4)
    device: Optional[Device] = None
    remote_address: str = ""
    _client_cache: Dict[str, Any] = field(default_factory=dict)
    
    def set_device(self, serial_number: str) -> None:
        """Set the device for this connection."""
        if serial_number and self.device is None:
            self.device = Device(serial_number=serial_number)
    
    def get_client_cache(self, key: str, default: Any = None) -> Any:
        """Get a value from the client cache."""
        return self._client_cache.get(key, default)
    
    def set_client_cache(self, key: str, value: Any) -> None:
        """Set a value in the client cache."""
        self._client_cache[key] = value
