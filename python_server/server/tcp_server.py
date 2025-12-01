"""TCP server for GPS device connections."""

import asyncio
import logging
from typing import Dict, Type, Optional, Callable, List
from uuid import uuid4

from .protocol import BaseProtocol
from .message_handler import BaseMessageHandler
from .data_message import DataMessage
from .message_input import MessageInput
from ..models.connection_context import ConnectionContext
from ..models.device_message import DeviceMessage

logger = logging.getLogger(__name__)

# Buffer size for reading data
BUFFER_SIZE = 4096


class TCPServer:
    """Multi-protocol TCP server for GPS devices."""
    
    def __init__(self):
        self._protocols: Dict[int, BaseProtocol] = {}
        self._handlers: Dict[Type[BaseProtocol], BaseMessageHandler] = {}
        self._servers: List[asyncio.Server] = []
        self._message_callback: Optional[Callable[[DeviceMessage, ConnectionContext], None]] = None
    
    def register_protocol(
        self, 
        protocol: BaseProtocol, 
        handler: BaseMessageHandler
    ) -> None:
        """Register a protocol and its handler."""
        self._protocols[protocol.port] = protocol
        self._handlers[type(protocol)] = handler
        logger.info(f"Registered {protocol.name} on port {protocol.port}")
    
    def on_message(self, callback: Callable[[DeviceMessage, ConnectionContext], None]) -> None:
        """Set callback for received messages."""
        self._message_callback = callback
    
    async def start(self, host: str = "0.0.0.0") -> None:
        """Start all protocol servers."""
        for port, protocol in self._protocols.items():
            server = await asyncio.start_server(
                lambda r, w, p=protocol: self._handle_connection(r, w, p),
                host,
                port
            )
            self._servers.append(server)
            logger.info(f"{protocol.name}: Listening on {host}:{port}")
        
        # Keep servers running
        await asyncio.gather(*[s.serve_forever() for s in self._servers])
    
    async def stop(self) -> None:
        """Stop all servers."""
        for server in self._servers:
            server.close()
            await server.wait_closed()
        self._servers.clear()
        logger.info("All servers stopped")
    
    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        protocol: BaseProtocol
    ) -> None:
        """Handle a single client connection."""
        peer = writer.get_extra_info('peername')
        connection_id = uuid4()
        
        context = ConnectionContext(
            protocol=protocol,
            connection_id=connection_id,
            remote_address=f"{peer[0]}:{peer[1]}" if peer else "unknown"
        )
        
        handler = self._handlers.get(type(protocol))
        if not handler:
            logger.error(f"No handler for {protocol.name}")
            writer.close()
            return
        
        logger.debug(f"{protocol.name}: Connected {context.remote_address}")
        
        try:
            buffer = b""
            
            while True:
                # Read data
                try:
                    data = await asyncio.wait_for(
                        reader.read(BUFFER_SIZE),
                        timeout=300  # 5 minute timeout
                    )
                except asyncio.TimeoutError:
                    logger.debug(f"{protocol.name}: Connection timeout")
                    break
                
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while buffer:
                    message_data, buffer = self._extract_message(buffer, protocol)
                    
                    if message_data is None:
                        break
                    
                    # Process the message
                    await self._process_message(
                        message_data, 
                        protocol, 
                        handler, 
                        context, 
                        writer
                    )
        
        except ConnectionResetError:
            logger.debug(f"{protocol.name}: Connection reset by client")
        except Exception as e:
            logger.error(f"{protocol.name}: Error handling connection: {e}")
        finally:
            logger.debug(f"{protocol.name}: Disconnected {context.remote_address}")
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
    
    def _extract_message(
        self, 
        buffer: bytes, 
        protocol: BaseProtocol
    ) -> tuple:
        """
        Extract a complete message from buffer.
        
        Returns (message_bytes, remaining_buffer) or (None, buffer) if incomplete.
        """
        if not buffer:
            return None, buffer
        
        # Check for message start
        start = protocol.message_start
        if start and not buffer.startswith(start):
            # Find start marker
            idx = buffer.find(start)
            if idx == -1:
                return None, buffer
            buffer = buffer[idx:]
        
        # Check for length-prefixed message
        msg_len = protocol.get_message_length(buffer, len(buffer))
        if msg_len is not None:
            if len(buffer) >= msg_len:
                return buffer[:msg_len], buffer[msg_len:]
            return None, buffer
        
        # Check for message end markers
        for end_marker in protocol.message_end:
            if end_marker:
                idx = buffer.find(end_marker)
                if idx != -1:
                    end_pos = idx + len(end_marker)
                    return buffer[:end_pos], buffer[end_pos:]
        
        # No complete message found
        return None, buffer
    
    async def _process_message(
        self,
        data: bytes,
        protocol: BaseProtocol,
        handler: BaseMessageHandler,
        context: ConnectionContext,
        writer: asyncio.StreamWriter
    ) -> None:
        """Process a complete message."""
        logger.debug(
            f"{protocol.name}: Received {len(data)} bytes from "
            f"{context.remote_address}"
        )
        
        # Create message input
        data_message = DataMessage(data, protocol.split_message_by)
        message_input = MessageInput(
            connection_context=context,
            data_message=data_message,
            writer=writer
        )
        
        # Parse message
        try:
            messages = handler.parse_range(message_input)
            
            if messages and context.device:
                for msg in messages:
                    if msg.is_valid_position():
                        logger.info(
                            f"{protocol.name}: Device {context.device.serial_number} - "
                            f"Lat: {msg.latitude}, Lon: {msg.longitude}, "
                            f"Speed: {msg.speed}"
                        )
                        
                        if self._message_callback:
                            self._message_callback(msg, context)
        
        except Exception as e:
            logger.debug(f"{protocol.name}: Parse error: {e}")
        
        # Flush any response data
        try:
            await writer.drain()
        except Exception:
            pass
