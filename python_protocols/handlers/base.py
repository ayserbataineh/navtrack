"""
Base Message Handler

This module defines the base class for all protocol message handlers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ..device_message import DeviceMessage


class BaseMessageHandler(ABC):
    """
    Base class for GPS protocol message handlers.
    
    All protocol-specific message handlers should extend this class
    and implement the abstract methods.
    """
    
    def __init__(self):
        """Initialize the message handler."""
        self.device_id: Optional[str] = None
    
    def parse(self, data: bytes) -> List[DeviceMessage]:
        """
        Parse raw data and return a list of device messages.
        
        Args:
            data: Raw byte data from the device
            
        Returns:
            List of parsed DeviceMessage objects
        """
        return self.parse_range(data)
    
    @abstractmethod
    def parse_range(self, data: bytes) -> List[DeviceMessage]:
        """
        Parse raw data and return a list of device messages.
        
        This is the main parsing method that should be implemented
        by each protocol handler.
        
        Args:
            data: Raw byte data from the device
            
        Returns:
            List of parsed DeviceMessage objects
        """
        pass
    
    def get_response(self, data: bytes) -> Optional[bytes]:
        """
        Generate a response to send back to the device.
        
        Some protocols require acknowledgment responses after receiving data.
        
        Args:
            data: The received data
            
        Returns:
            Response bytes to send, or None if no response needed
        """
        return None
    
    def is_authenticated(self) -> bool:
        """
        Check if the device has been authenticated.
        
        Returns:
            True if device is authenticated, False otherwise
        """
        return self.device_id is not None
    
    def set_device_id(self, device_id: str) -> None:
        """
        Set the device ID after authentication.
        
        Args:
            device_id: The device identifier (IMEI or serial number)
        """
        self.device_id = device_id
