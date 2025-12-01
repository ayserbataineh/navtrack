"""Device message model for GPS tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class DeviceMessage:
    """Represents a GPS message from a tracking device."""
    
    # Timestamp
    date: Optional[datetime] = None
    
    # Location data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    speed: Optional[int] = None
    heading: Optional[int] = None
    satellites: Optional[int] = None
    valid: Optional[bool] = None
    
    # Precision
    pdop: Optional[float] = None
    hdop: Optional[float] = None
    
    # Device info
    device_odometer: Optional[int] = None  # meters
    device_battery_level: Optional[int] = None  # 0-100%
    device_battery_voltage: Optional[float] = None  # V
    device_battery_current: Optional[float] = None  # A
    
    # Vehicle info
    vehicle_odometer: Optional[int] = None  # km
    vehicle_ignition: Optional[bool] = None
    vehicle_ignition_duration: Optional[int] = None  # seconds
    vehicle_fuel_consumption: Optional[float] = None
    vehicle_voltage: Optional[float] = None
    
    # GSM info
    gsm_signal_strength: Optional[int] = None  # TS 27.007 values
    gsm_signal_level: Optional[int] = None  # 1-5
    gsm_mobile_country_code: Optional[str] = None
    gsm_mobile_network_code: Optional[str] = None
    gsm_location_area_code: Optional[str] = None
    gsm_cell_id: Optional[int] = None
    gsm_lte_cell_id: Optional[int] = None
    
    # Additional data
    additional_data: Dict[str, str] = field(default_factory=dict)
    
    def is_valid_position(self) -> bool:
        """Check if the position data is valid."""
        if self.latitude is None or self.longitude is None:
            return False
        if not (-90 <= self.latitude <= 90):
            return False
        if not (-180 <= self.longitude <= 180):
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result
