"""
Device Message Data Structure

This module defines the DeviceMessage class that represents GPS tracking data
received from devices. It mirrors the structure used in the C# implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict


@dataclass
class DeviceMessage:
    """
    Represents a GPS device message with location and telemetry data.
    
    This class mirrors the DeviceMessageEntity from the C# implementation
    and contains all the standard fields for GPS tracking data.
    
    Attributes:
        date: The timestamp of the GPS fix
        latitude: Latitude coordinate in decimal degrees
        longitude: Longitude coordinate in decimal degrees
        speed: Speed in km/h
        heading: Heading/course in degrees (0-360)
        altitude: Altitude in meters
        satellites: Number of satellites used for fix
        pdop: Position Dilution of Precision
        hdop: Horizontal Dilution of Precision
        valid: Whether the GPS fix is valid
        device_odometer: Odometer reading from device in meters
        device_battery_level: Battery level (0-100%)
        device_battery_voltage: Battery voltage in Volts
        device_battery_current: Battery current in Amps
        vehicle_odometer: Vehicle odometer in km
        vehicle_ignition: Ignition state (True/False)
        vehicle_ignition_duration: Duration of ignition ON in seconds
        vehicle_fuel_consumption: Fuel consumption
        vehicle_voltage: Vehicle voltage in Volts
        gsm_signal_strength: GSM signal strength per TS 27.007
        gsm_signal_level: GSM signal level (1-5)
        gsm_mobile_country_code: Mobile Country Code
        gsm_mobile_network_code: Mobile Network Code
        gsm_location_area_code: Location Area Code
        gsm_cell_id: GSM Cell ID
        gsm_lte_cell_id: LTE Cell ID
        message_priority: Message priority level
        additional_data: Additional protocol-specific data
    """
    
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
    
    # Device telemetry
    device_odometer: Optional[int] = None  # meters
    device_battery_level: Optional[int] = None  # 0-100%
    device_battery_voltage: Optional[float] = None  # Volts
    device_battery_current: Optional[float] = None  # Amps
    
    # Vehicle data
    vehicle_odometer: Optional[int] = None  # km
    vehicle_ignition: Optional[bool] = None
    vehicle_ignition_duration: Optional[int] = None  # seconds
    vehicle_fuel_consumption: Optional[float] = None
    vehicle_voltage: Optional[float] = None  # Volts
    
    # GSM/Cellular data
    gsm_signal_strength: Optional[int] = None  # TS 27.007 values
    gsm_signal_level: Optional[int] = None  # 1-5
    gsm_mobile_country_code: Optional[str] = None
    gsm_mobile_network_code: Optional[str] = None
    gsm_location_area_code: Optional[str] = None
    gsm_cell_id: Optional[int] = None
    gsm_lte_cell_id: Optional[int] = None
    
    # Message metadata
    message_priority: Optional[str] = None  # Normal, High, Emergency
    
    # Additional protocol-specific data
    additional_data: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert the message to a dictionary."""
        return {
            "date": self.date.isoformat() if self.date else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "heading": self.heading,
            "altitude": self.altitude,
            "satellites": self.satellites,
            "pdop": self.pdop,
            "hdop": self.hdop,
            "valid": self.valid,
            "device_odometer": self.device_odometer,
            "device_battery_level": self.device_battery_level,
            "device_battery_voltage": self.device_battery_voltage,
            "device_battery_current": self.device_battery_current,
            "vehicle_odometer": self.vehicle_odometer,
            "vehicle_ignition": self.vehicle_ignition,
            "vehicle_ignition_duration": self.vehicle_ignition_duration,
            "vehicle_fuel_consumption": self.vehicle_fuel_consumption,
            "vehicle_voltage": self.vehicle_voltage,
            "gsm_signal_strength": self.gsm_signal_strength,
            "gsm_signal_level": self.gsm_signal_level,
            "gsm_mobile_country_code": self.gsm_mobile_country_code,
            "gsm_mobile_network_code": self.gsm_mobile_network_code,
            "gsm_location_area_code": self.gsm_location_area_code,
            "gsm_cell_id": self.gsm_cell_id,
            "gsm_lte_cell_id": self.gsm_lte_cell_id,
            "message_priority": self.message_priority,
            "additional_data": self.additional_data,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DeviceMessage":
        """Create a DeviceMessage from a dictionary."""
        msg = cls()
        if data.get("date"):
            msg.date = datetime.fromisoformat(data["date"])
        msg.latitude = data.get("latitude", 0.0)
        msg.longitude = data.get("longitude", 0.0)
        msg.speed = data.get("speed")
        msg.heading = data.get("heading")
        msg.altitude = data.get("altitude")
        msg.satellites = data.get("satellites")
        msg.pdop = data.get("pdop")
        msg.hdop = data.get("hdop")
        msg.valid = data.get("valid")
        msg.device_odometer = data.get("device_odometer")
        msg.device_battery_level = data.get("device_battery_level")
        msg.device_battery_voltage = data.get("device_battery_voltage")
        msg.device_battery_current = data.get("device_battery_current")
        msg.vehicle_odometer = data.get("vehicle_odometer")
        msg.vehicle_ignition = data.get("vehicle_ignition")
        msg.vehicle_ignition_duration = data.get("vehicle_ignition_duration")
        msg.vehicle_fuel_consumption = data.get("vehicle_fuel_consumption")
        msg.vehicle_voltage = data.get("vehicle_voltage")
        msg.gsm_signal_strength = data.get("gsm_signal_strength")
        msg.gsm_signal_level = data.get("gsm_signal_level")
        msg.gsm_mobile_country_code = data.get("gsm_mobile_country_code")
        msg.gsm_mobile_network_code = data.get("gsm_mobile_network_code")
        msg.gsm_location_area_code = data.get("gsm_location_area_code")
        msg.gsm_cell_id = data.get("gsm_cell_id")
        msg.gsm_lte_cell_id = data.get("gsm_lte_cell_id")
        msg.message_priority = data.get("message_priority")
        msg.additional_data = data.get("additional_data", {})
        return msg
