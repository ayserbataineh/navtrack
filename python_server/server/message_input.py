"""Message input for protocol handlers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from .data_message import DataMessage
    from ..models.connection_context import ConnectionContext


@dataclass
class MessageInput:
    """Input data for message handlers."""
    
    connection_context: 'ConnectionContext'
    data_message: 'DataMessage'
    writer: asyncio.StreamWriter
    
    def write(self, data: bytes) -> None:
        """Write data back to the device."""
        self.writer.write(data)
    
    def write_string(self, data: str) -> None:
        """Write string data back to the device."""
        self.writer.write(data.encode('ascii'))
