"""Device model for GPS tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Device:
    """Represents a GPS tracking device."""
    
    serial_number: str
    asset_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    max_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate device after initialization."""
        if not self.serial_number:
            raise ValueError("Serial number cannot be empty")
