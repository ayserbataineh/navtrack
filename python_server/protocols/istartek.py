"""iStartek GPS protocol implementation."""

from typing import Optional, List

from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..server.message_input import MessageInput
from ..models.device_message import DeviceMessage
from ..helpers.gprmc import GPRMC


class iStartekProtocol(BaseProtocol):
    """iStartek GPS tracker protocol (VT900, VT200, VT380, etc.)."""
    
    @property
    def port(self) -> int:
        return 7018
    
    @property
    def message_start(self) -> bytes:
        return b"$$"
    
    @property
    def message_end(self) -> List[bytes]:
        return [b"\r\n"]


class iStartekMessageHandler(BaseMessageHandler):
    """Message handler for iStartek protocol."""
    
    def parse(self, input_data: MessageInput) -> Optional[DeviceMessage]:
        """Parse iStartek GPS message."""
        msg = input_data.data_message.string
        
        if len(msg) < 17:
            return None
        
        try:
            # Extract data portion (skip header and checksum)
            data = msg[13:-4]
            
            # Find GPRMC data (up to first |)
            pipe_idx = data.find('|')
            gprmc_str = data[:pipe_idx] if pipe_idx > 0 else data
            
            # Parse GPRMC
            gprmc = GPRMC.parse(gprmc_str)
            if not gprmc:
                return None
            
            # Extract IMEI from header (bytes 4-11, hex encoded)
            hex_data = input_data.data_message.hex
            if len(hex_data) >= 11:
                imei = "".join(hex_data[4:11]).rstrip('F')
                input_data.connection_context.set_device(imei)
            
            # Parse additional data from bar-separated fields
            bar_parts = input_data.data_message.bar_split
            heading = self._safe_int(bar_parts[1]) if len(bar_parts) > 1 else None
            altitude = self._safe_int(bar_parts[2]) if len(bar_parts) > 2 else None
            
            return DeviceMessage(
                date=gprmc.datetime,
                latitude=gprmc.latitude,
                longitude=gprmc.longitude,
                speed=gprmc.speed,
                valid=gprmc.position_status,
                heading=heading,
                altitude=altitude
            )
            
        except Exception:
            return None
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int."""
        try:
            return int(float(value)) if value else None
        except (ValueError, TypeError):
            return None
