from abc import ABC, abstractmethod
from typing import List, Optional, Any

class BaseProtocol(ABC):
    @property
    @abstractmethod
    def port(self) -> int:
        pass

    def get_message_length(self, buffer: bytes, bytes_read_count: int) -> Optional[int]:
        # Default implementation, can be overridden
        return None

class MessageInput:
    def __init__(self, connection_context, data_message, network_stream):
        self.connection_context = connection_context
        self.data_message = data_message
        self.network_stream = network_stream

class ICustomMessageHandler(ABC):
    @abstractmethod
    def parse_range(self, input_data: MessageInput) -> Optional[List[Any]]:
        pass

class BaseMessageHandler(ICustomMessageHandler):
    # Common functionality can be added here
    pass
