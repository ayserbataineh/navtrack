"""
Teltonika Protocol Message Handler

This module implements the message handler for Teltonika GPS trackers.
Supports Codec 8, Codec 8 Extended, and Codec 16.

Protocol Specification:
- Binary protocol
- TCP/UDP communication
- Supports multiple data packets in a single message
- CRC verification

Message Format:
- 4 bytes: Preamble (0x00000000)
- 4 bytes: Data field length
- 1 byte: Codec ID
- 1 byte: Number of data packets
- N bytes: Data packets
- 1 byte: Number of data packets (repeated)
- 4 bytes: CRC-16
"""

from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Dict
from ..device_message import DeviceMessage
from ..utils import ByteReader, bytes_to_hex
from .base import BaseMessageHandler


class TeltonikaCodec(IntEnum):
    """Teltonika codec types."""
    CODEC_8 = 0x08
    CODEC_8_EXTENDED = 0x8E
    CODEC_16 = 0x10


class TeltonikaDataIds(IntEnum):
    """Teltonika AVL data element IDs."""
    # Permanent I/O elements
    DIGITAL_INPUT_1 = 1
    ICCID1 = 11
    ICCID2 = 14
    ECO_SCORE = 15
    TOTAL_ODOMETER = 16
    GSM_SIGNAL = 21
    GNSS_SPEED = 24
    EXTERNAL_VOLTAGE = 66
    BATTERY_VOLTAGE = 67
    BATTERY_CURRENT = 68
    GNSS_STATUS = 69
    BATTERY_LEVEL = 113
    GNSS_PDOP = 181
    GNSS_HDOP = 182
    TRIP_ODOMETER = 199
    SLEEP_MODE = 200
    GSM_CELL_ID = 205
    GSM_AREA_CODE = 206
    IGNITION = 239
    MOVEMENT = 240
    ACTIVE_GSM_OPERATOR = 241
    UMTS_LTE_CELL_ID = 636
    
    # Event I/O elements
    EVENT_TRIP = 250
    IGNITION_ON_COUNTER = 449
    
    # OBD elements
    OBD_DTC_COUNT = 30
    OBD_ENGINE_LOAD = 31
    OBD_COOLANT_TEMP = 32
    OBD_ENGINE_RPM = 36
    OBD_SPEED = 37
    OBD_FUEL_LEVEL = 48
    OBD_VIN = 256
    OBD_FAULT_CODES = 281
    
    # OBD OEM elements
    OBD_OEM_MILEAGE = 389
    OBD_OEM_FUEL_LEVEL = 390
    
    # CAN adapters
    CAN_DOOR_STATUS = 90
    CAN_FUEL_CONSUMED = 102
    CAN_CONTROL_STATE = 123


class TeltonikaCodecConfig:
    """Configuration for different Teltonika codecs."""
    
    def __init__(
        self,
        main_event_id_length: int = 1,
        data_packet_id_bytes: int = 1,
        data_packet_bytes: int = 1,
        data_packet_count_bytes: int = 1,
        has_generation_type: bool = False,
        has_variable_data_packets: bool = False
    ):
        self.main_event_id_length = main_event_id_length
        self.data_packet_id_bytes = data_packet_id_bytes
        self.data_packet_bytes = data_packet_bytes
        self.data_packet_count_bytes = data_packet_count_bytes
        self.has_generation_type = has_generation_type
        self.has_variable_data_packets = has_variable_data_packets


# Codec configurations
CODEC_CONFIGS: Dict[TeltonikaCodec, TeltonikaCodecConfig] = {
    TeltonikaCodec.CODEC_8: TeltonikaCodecConfig(
        main_event_id_length=1,
        data_packet_id_bytes=1,
        data_packet_bytes=1,
        data_packet_count_bytes=1
    ),
    TeltonikaCodec.CODEC_8_EXTENDED: TeltonikaCodecConfig(
        main_event_id_length=2,
        data_packet_id_bytes=2,
        data_packet_bytes=2,
        data_packet_count_bytes=2,
        has_variable_data_packets=True
    ),
    TeltonikaCodec.CODEC_16: TeltonikaCodecConfig(
        main_event_id_length=2,
        data_packet_id_bytes=2,
        data_packet_bytes=2,
        data_packet_count_bytes=2,
        has_generation_type=True,
        has_variable_data_packets=True
    )
}


class TeltonikaMessageHandler(BaseMessageHandler):
    """
    Message handler for Teltonika GPS trackers.
    
    Supports:
    - FMB series (FMB920, FMB140, FMB120, etc.)
    - FMC series (FMC130)
    - FMU series (FMU130)
    - FM series (FM3001)
    - FMT series (FMT100)
    
    Protocol features:
    - Binary message format
    - Multiple codec support (8, 8E, 16)
    - Batch location reporting
    - OBD/CAN data support
    """
    
    def __init__(self):
        super().__init__()
        self.codec_config: Optional[TeltonikaCodecConfig] = None
    
    def parse_range(self, data: bytes) -> List[DeviceMessage]:
        """
        Parse Teltonika message data.
        
        Args:
            data: Raw byte data from the device
            
        Returns:
            List of parsed DeviceMessage objects
        """
        # Check for IMEI message (authentication)
        if len(data) > 16 and data[0] == 0x00 and data[1] == 0x0F:
            # IMEI message format: 2 bytes length + 15 bytes IMEI
            imei = data[2:17].decode('ascii')
            self.set_device_id(imei)
            return []
        
        # Not authenticated yet
        if not self.is_authenticated():
            return []
        
        return self._parse_data_message(data)
    
    def _parse_data_message(self, data: bytes) -> List[DeviceMessage]:
        """Parse a data message containing location data."""
        messages = []
        reader = ByteReader(data)
        
        # Get codec configuration
        codec_config = self._get_codec(reader)
        if not codec_config:
            return []
        
        self.codec_config = codec_config
        
        # Number of locations
        num_locations = reader.get_one()
        
        for _ in range(num_locations):
            message = self._parse_position(reader)
            messages.append(message)
        
        return messages
    
    def _get_codec(self, reader: ByteReader) -> Optional[TeltonikaCodecConfig]:
        """Get the codec configuration from the message."""
        # Skip preamble (4 bytes)
        reader.skip(4)
        # Skip data length (4 bytes)
        reader.skip(4)
        # Read codec ID
        codec_id = reader.get_one()
        
        try:
            codec = TeltonikaCodec(codec_id)
            return CODEC_CONFIGS.get(codec)
        except ValueError:
            return None
    
    def _parse_position(self, reader: ByteReader) -> DeviceMessage:
        """Parse a single position record."""
        message = DeviceMessage()
        message.additional_data = {}
        
        # Timestamp (8 bytes, milliseconds since epoch)
        timestamp = reader.get_ulong()
        message.date = datetime.utcfromtimestamp(timestamp / 1000)
        
        # Priority (1 byte)
        priority = reader.get_one()
        if priority == 1:
            message.message_priority = "High"
        elif priority == 2:
            message.message_priority = "Emergency"
        
        # Coordinates
        message.longitude = self._get_coordinate(reader.get(4))
        message.latitude = self._get_coordinate(reader.get(4))
        
        # Altitude (2 bytes)
        message.altitude = reader.get_short()
        
        # Heading (2 bytes)
        message.heading = reader.get_ushort()
        
        # Satellites (1 byte)
        message.satellites = reader.get_one()
        
        # Speed (2 bytes)
        message.speed = reader.get_ushort()
        
        # Event ID
        if self.codec_config.main_event_id_length == 2:
            event_id = reader.get_ushort()
        else:
            event_id = reader.get_one()
        message.additional_data["event_id"] = str(event_id)
        
        # Generation type (Codec 16 only)
        if self.codec_config.has_generation_type:
            reader.skip(1)
        
        # Data packet count
        reader.skip(self.codec_config.data_packet_count_bytes)
        
        # Parse I/O elements
        self._parse_io_elements(reader, message, 1)  # 1-byte values
        self._parse_io_elements(reader, message, 2)  # 2-byte values
        self._parse_io_elements(reader, message, 4)  # 4-byte values
        self._parse_io_elements(reader, message, 8)  # 8-byte values
        
        # Variable length elements (Codec 8E and 16)
        if self.codec_config.has_variable_data_packets:
            self._parse_variable_io_elements(reader, message)
        
        return message
    
    def _get_coordinate(self, data: bytes) -> float:
        """Convert 4-byte coordinate to decimal degrees."""
        value = int.from_bytes(data, byteorder='big', signed=True)
        return value / 10000000.0
    
    def _parse_io_elements(self, reader: ByteReader, message: DeviceMessage, value_bytes: int) -> None:
        """Parse I/O elements of a specific size."""
        if self.codec_config.data_packet_bytes == 1:
            count = reader.get_one()
        else:
            count = reader.get_ushort()
        
        for _ in range(count):
            if self.codec_config.data_packet_id_bytes == 1:
                element_id = reader.get_one()
            else:
                element_id = reader.get_ushort()
            
            value = reader.get(value_bytes)
            self._map_io_element(element_id, value, message)
    
    def _parse_variable_io_elements(self, reader: ByteReader, message: DeviceMessage) -> None:
        """Parse variable-length I/O elements."""
        count = reader.get_ushort()
        
        for _ in range(count):
            element_id = reader.get_ushort()
            length = reader.get_ushort()
            value = reader.get(length)
            self._map_io_element(element_id, value, message)
    
    def _map_io_element(self, element_id: int, value: bytes, message: DeviceMessage) -> None:
        """Map I/O element ID to device message field."""
        try:
            int_value = int.from_bytes(value, byteorder='big')
            
            if element_id == TeltonikaDataIds.TOTAL_ODOMETER:
                message.device_odometer = int_value
            elif element_id == TeltonikaDataIds.GSM_SIGNAL:
                message.gsm_signal_level = int_value
            elif element_id == TeltonikaDataIds.EXTERNAL_VOLTAGE:
                message.vehicle_voltage = int_value * 0.001
            elif element_id == TeltonikaDataIds.BATTERY_VOLTAGE:
                message.device_battery_voltage = int_value * 0.001
            elif element_id == TeltonikaDataIds.BATTERY_CURRENT:
                message.device_battery_current = int_value * 0.001
            elif element_id == TeltonikaDataIds.BATTERY_LEVEL:
                message.device_battery_level = int_value
            elif element_id == TeltonikaDataIds.GNSS_PDOP:
                message.pdop = int_value * 0.1
            elif element_id == TeltonikaDataIds.GNSS_HDOP:
                message.hdop = int_value * 0.1
            elif element_id == TeltonikaDataIds.IGNITION:
                message.vehicle_ignition = int_value == 1
            elif element_id == TeltonikaDataIds.IGNITION_ON_COUNTER:
                message.vehicle_ignition_duration = int_value
            elif element_id == TeltonikaDataIds.GNSS_STATUS:
                message.valid = int_value == 1
                message.additional_data["gnss_status"] = str(int_value)
            elif element_id == TeltonikaDataIds.ACTIVE_GSM_OPERATOR:
                hni = str(int_value)
                if len(hni) > 4:
                    message.gsm_mobile_country_code = hni[:3]
                    message.gsm_mobile_network_code = hni[3:]
            elif element_id == TeltonikaDataIds.OBD_OEM_MILEAGE:
                message.vehicle_odometer = int_value
            elif element_id == TeltonikaDataIds.CAN_FUEL_CONSUMED:
                message.vehicle_fuel_consumption = int_value * 0.1
            else:
                # Store unknown elements in additional data
                message.additional_data[str(element_id)] = bytes_to_hex(value)
        except (ValueError, IndexError):
            pass
    
    def get_response(self, data: bytes) -> Optional[bytes]:
        """
        Generate response for Teltonika device.
        
        For IMEI message: returns 0x01 (accept)
        For data message: returns number of data received
        """
        # IMEI message response
        if len(data) > 16 and data[0] == 0x00 and data[1] == 0x0F:
            return bytes([0x01])
        
        # Data message response
        if len(data) > 8 and data[0:4] == bytes([0, 0, 0, 0]):
            reader = ByteReader(data)
            reader.skip(4)  # preamble
            reader.skip(4)  # length
            reader.skip(1)  # codec
            num_data = reader.get_one()
            # Return number of data packets received as 4 bytes
            return num_data.to_bytes(4, byteorder='big')
        
        return None
