# Navtrack Python Protocols

This module provides Python implementations of GPS tracking device protocols extracted from the Navtrack platform. It includes protocol definitions, message parsing utilities, and data structures for GPS tracking data.

## Installation

The module is a pure Python package with no external dependencies for the core functionality.

```python
# Add the python_protocols directory to your Python path
import sys
sys.path.append('/path/to/navtrack')

from python_protocols import get_all_protocols, get_protocol, DeviceMessage
```

## Supported Protocols

The following GPS tracking protocols are supported:

| Protocol | Port | Manufacturer | Message Format |
|----------|------|--------------|----------------|
| Meitrack | 7001 | Meitrack | Binary |
| Teltonika | 7002 | Teltonika | Binary |
| Meiligao | 7003 | Meiligao | Binary |
| Megastek | 7004 | Megastek | Text |
| Totem | 7005 | Totem | Text/Binary |
| Tzone | 7006 | Tzone | Text |
| Coban | 7007 | Coban | Text |
| Queclink | 7008 | Queclink | Text |
| Fifotrack | 7009 | Fifotrack | Text |
| Suntech | 7010 | Suntech | Text |
| TkStar | 7011 | TkStar | Text |
| SinoTrack | 7012 | SinoTrack | Text |
| Concox | 7013 | Concox | Binary |
| CanTrack | 7014 | CanTrack | Text |
| LKGPS | 7015 | LKGPS | Text |
| Carscop | 7016 | Carscop | Text |
| Xexun | 7017 | Xexun | Text |
| iStartek | 7018 | iStartek | Text |
| XeElectech | 7019 | XeElectech | Text |
| VjoyCar | 7020 | VjoyCar | Text |
| Eelink | 7021 | Eelink | Binary |
| Gosafe | 7022 | Gosafe | Text |
| Skypatrol | 7023 | Skypatrol | Text |
| Xirgo | 7024 | Xirgo | Text |
| Smartrack | 7025 | Smartrack | Text |
| ReachFar | 7026 | ReachFar | Text |
| iCarGPS | 7027 | iCarGPS | Text |
| iTracGPS | 7028 | iTracGPS | Text |
| Alematics | 7029 | Alematics | Text |
| Pretrace | 7030 | Pretrace | Text |
| Arknav | 7031 | Arknav | Text |
| Haicom | 7032 | Haicom | Text |
| CarTrackGPS | 7033 | CarTrackGPS | Text |
| KingSword | 7034 | KingSword | Text |
| Amwell | 7035 | Amwell | Text |
| Sanav | 7036 | Sanav | Text |
| Gotop | 7037 | Gotop | Text |
| GlobalSat | 7038 | GlobalSat | Text |
| GoPass | 7039 | GoPass | Text |
| Jointech | 7040 | Jointech | Text |
| KeSon | 7041 | KeSon | Text |
| Bofan | 7042 | Bofan | Text |
| VSun | 7043 | VSun | Text |
| BlueIdea | 7044 | BlueIdea | Text |
| ManPower | 7045 | ManPower | Text |
| WondeProud | 7046 | WondeProud | Text |
| GPSMarker | 7047 | GPSMarker | Text |
| Eview | 7048 | Eview | Text |
| Freedom | 7049 | Freedom | Text |
| Topfly | 7050 | Topfly | Text |
| ERM (StarLink) | 7051 | StarLink | Text |
| Laipac | 7052 | Laipac | Text |
| Navtelecom | 7054 | Navtelecom | Binary |
| Galileosky | 7055 | Galileosky | Binary |
| Ruptela | 7056 | Ruptela | Binary |
| Arusnavi | 7057 | Arusnavi | Binary |
| Neomatica | 7058 | Neomatica | Binary |
| Satellite | 7059 | Satellite | Binary |
| Autofon | 7060 | Autofon | Binary |
| ATrack | 7061 | ATrack | Binary/Text |

## Usage Examples

### Getting Protocol Information

```python
from python_protocols import get_all_protocols, get_protocol

# Get all protocols
protocols = get_all_protocols()
for protocol in protocols:
    print(f"{protocol.name}: Port {protocol.port}")

# Get a specific protocol
teltonika = get_protocol("Teltonika")
print(f"Port: {teltonika.port}")
print(f"Custom length handling: {teltonika.has_custom_length}")
```

### Parsing Messages

```python
from python_protocols.handlers import TeltonikaMessageHandler, CobanMessageHandler

# Teltonika device
teltonika_handler = TeltonikaMessageHandler()

# Receive IMEI authentication message
imei_data = bytes.fromhex("000F333536333037303432343431303133")
messages = teltonika_handler.parse(imei_data)
response = teltonika_handler.get_response(imei_data)  # Returns 0x01

# Receive location data
location_data = bytes.fromhex("000000000000003608010000016B40D8EA30010000000000000000000000000000000105021503010101425E0F01F10000601A014E0000000000000000010000C7CF")
messages = teltonika_handler.parse(location_data)
for msg in messages:
    print(f"Date: {msg.date}")
    print(f"Lat: {msg.latitude}, Lon: {msg.longitude}")
    print(f"Speed: {msg.speed} km/h")

# Coban device
coban_handler = CobanMessageHandler()

# Authentication
auth_data = b"##,imei:359586015829802,A;"
coban_handler.parse(auth_data)
response = coban_handler.get_response(auth_data)  # Returns b'LOAD'

# Location
location_data = b"imei:359587010124900,tracker,0809231929,13554900601,F,112909.397,A,2234.4669,N,11354.3287,E,0.11,;"
messages = coban_handler.parse(location_data)
```

### Working with Device Messages

```python
from python_protocols import DeviceMessage

# Create a message
message = DeviceMessage()
message.date = datetime.now()
message.latitude = 46.7976
message.longitude = 23.2759
message.speed = 65
message.heading = 180
message.valid = True

# Convert to dictionary
data = message.to_dict()

# Create from dictionary
msg = DeviceMessage.from_dict(data)
```

## Protocol Specifications

### Message Framing

Each protocol has specific message framing rules:

- **Message Start**: Bytes that indicate the start of a message (e.g., `0x78 0x78` for Concox)
- **Message End**: Bytes that indicate the end of a message (e.g., `0x0D 0x0A` for CRLF)
- **Split By**: Character used to split multiple messages (e.g., `;` for Suntech)
- **Custom Length**: Some protocols encode message length in the header

### Data Fields

Standard GPS tracking data fields:

| Field | Type | Description |
|-------|------|-------------|
| date | datetime | Timestamp of the GPS fix |
| latitude | float | Latitude in decimal degrees |
| longitude | float | Longitude in decimal degrees |
| speed | int | Speed in km/h |
| heading | int | Course/heading in degrees (0-360) |
| altitude | int | Altitude in meters |
| satellites | int | Number of satellites used |
| pdop | float | Position Dilution of Precision |
| hdop | float | Horizontal Dilution of Precision |
| valid | bool | GPS fix validity |
| device_odometer | int | Device odometer in meters |
| device_battery_level | int | Battery percentage (0-100) |
| device_battery_voltage | float | Battery voltage in Volts |
| vehicle_ignition | bool | Ignition state |
| vehicle_odometer | int | Vehicle odometer in km |
| gsm_signal_level | int | GSM signal level (1-5) |

## Utility Functions

The `utils` module provides helper functions:

```python
from python_protocols.utils import (
    convert_dmm_lat_to_decimal,
    convert_dmm_long_to_decimal,
    knots_to_kph,
    parse_datetime_yymmddhhmmss,
    ByteReader,
    MessageReader,
    calculate_crc16,
)

# Convert coordinates
lat = convert_dmm_lat_to_decimal("2234.4669", "N")  # 22.574448

# Convert speed
speed_kph = knots_to_kph(25.5)  # 47.226 km/h

# Read binary data
reader = ByteReader(data)
timestamp = reader.get_ulong()
lat = reader.get_int() / 10000000.0

# Calculate CRC
crc = calculate_crc16(data)
```

## Adding New Protocols

To add support for a new protocol:

1. Create a new protocol class in `protocols.py`:

```python
class NewProtocol(Protocol):
    def __init__(self):
        super().__init__(
            name="NewProtocol",
            port=7XXX,
            message_start=bytes([0xAA, 0xBB]),
            message_end=[bytes([0x0D, 0x0A])],
            description="New GPS tracking protocol",
            manufacturer="Manufacturer"
        )
```

2. Create a message handler in `handlers/`:

```python
from .base import BaseMessageHandler

class NewProtocolMessageHandler(BaseMessageHandler):
    def parse_range(self, data: bytes) -> List[DeviceMessage]:
        # Implement parsing logic
        pass
```

3. Register the protocol in the `_register_protocols()` function.

## License

This module is part of the Navtrack project and is licensed under the same terms.

## Contributing

Contributions are welcome! Please ensure that:

1. New protocols follow the existing code structure
2. Message handlers include proper error handling
3. Documentation is updated for new protocols
4. Test cases are provided for new functionality
