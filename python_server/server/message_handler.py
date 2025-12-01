"""Base message handler for GPS protocols."""

from abc import ABC
from typing import Optional, List, Callable, TYPE_CHECKING

from ..models.device_message import DeviceMessage

if TYPE_CHECKING:
    from .message_input import MessageInput


class BaseMessageHandler(ABC):
    """Base class for protocol message handlers."""
    
    def parse(self, input_data: 'MessageInput') -> Optional[DeviceMessage]:
        """
        Parse a single message.
        
        Override this method to implement protocol-specific parsing.
        """
        return None
    
    def parse_range(self, input_data: 'MessageInput') -> Optional[List[DeviceMessage]]:
        """
        Parse message that may contain multiple positions.
        
        Default implementation calls parse() for single message.
        """
        try:
            message = self.parse(input_data)
            if message:
                return [message]
        except Exception:
            pass
        return None
    
    def parse_with_handlers(
        self, 
        input_data: 'MessageInput',
        *parsers: Callable[['MessageInput'], Optional[DeviceMessage]]
    ) -> Optional[DeviceMessage]:
        """
        Try multiple parsers until one succeeds.
        
        Resets message readers between attempts.
        """
        for parser in parsers:
            try:
                input_data.data_message.reader.reset()
                input_data.data_message.byte_reader.reset()
                
                result = parser(input_data)
                if result is not None:
                    return result
            except Exception:
                pass
        
        return None
    
    def parse_range_with_handlers(
        self,
        input_data: 'MessageInput',
        *parsers: Callable[['MessageInput'], Optional[List[DeviceMessage]]]
    ) -> Optional[List[DeviceMessage]]:
        """
        Try multiple range parsers until one succeeds.
        """
        for parser in parsers:
            try:
                input_data.data_message.reader.reset()
                input_data.data_message.byte_reader.reset()
                
                result = parser(input_data)
                if result is not None:
                    return result
            except Exception:
                pass
        
        return None
