from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

@dataclass
class DeviceMessageEntity:
    asset_id: Optional[str] = None
    device_id: Optional[str] = None
    connection_id: Optional[str] = None
    created_date: Optional[datetime] = None
    message_priority: Optional[str] = None  # Enum in C#
    date: Optional[datetime] = None

    latitude: float = 0.0
    longitude: float = 0.0

    speed: Optional[int] = None
    heading: Optional[int] = None
    altitude: Optional[int] = None
    satellites: Optional[int] = None
    pdop: Optional[float] = None
    hdop: Optional[float] = None
    valid: Optional[bool] = None

    device_odometer: Optional[int] = None
    device_battery_level: Optional[int] = None
    device_battery_voltage: Optional[float] = None
    device_battery_current: Optional[float] = None

    vehicle_odometer: Optional[int] = None
    vehicle_ignition: Optional[bool] = None
    vehicle_ignition_duration: Optional[int] = None
    vehicle_fuel_consumption: Optional[float] = None
    vehicle_voltage: Optional[float] = None

    gsm_signal_strength: Optional[int] = None
    gsm_signal_level: Optional[int] = None
    gsm_mobile_country_code: Optional[str] = None
    gsm_mobile_network_code: Optional[str] = None
    gsm_location_area_code: Optional[str] = None
    gsm_cell_id: Optional[int] = None
    gsm_lte_cell_id: Optional[int] = None

    old_id: Optional[str] = None

    additional_data_dic: Dict[str, str] = field(default_factory=dict)
    additional_data: Optional[str] = None
