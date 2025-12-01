"""Navtelecom GPS protocol implementation."""

import struct
from typing import Optional, List
from datetime import datetime

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage


class NavtelecomProtocol(BaseProtocol):
    """Navtelecom GPS tracker protocol (SIGNAL S-2550, S-2551, etc.)."""
    
    @property
    def port(self) -> int:
        return 7054


class NavtelecomMessageHandler(BaseMessageHandler):
    """Message handler for Navtelecom protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        data = input_data.data_message.bytes
        if len(data) < 10:
            return None
        
        # Binary protocol - extract IMEI from header
        try:
            if len(data) >= 15:
                imei = data[0:15].decode('ascii', errors='ignore')
                if imei.isdigit():
                    input_data.connection_context.set_device(imei)
        except Exception:
            pass
        
        # Try to parse position data
        return self._parse_binary(data)
    
    def _parse_binary(self, data: bytes) -> Optional[DeviceMessage]:
        """Parse binary position data."""
        try:
            # Navtelecom binary format varies by device model
            # This is a basic implementation
            if len(data) >= 30:
                # Attempt to find coordinates in the data
                # This would need protocol documentation for full implementation
                pass
        except Exception:
            pass
        return None
