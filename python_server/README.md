# Navtrack Python GPS Tracking Server

A standalone Python implementation of the Navtrack GPS protocol listener, supporting 60+ GPS device protocols. This server allows direct device connections for GPS tracking.

## Features

- **60+ Supported Protocols**: Compatible with most popular GPS tracking devices
- **Async TCP Server**: High-performance asyncio-based server
- **Multi-Protocol Support**: Run multiple protocols on different ports simultaneously
- **Easy Integration**: Simple callback system for processing received positions
- **Extensible**: Easy to add new protocols
- **Standalone**: No external dependencies on databases or message queues

## Supported Devices

The server supports the following GPS tracker protocols (and their associated devices):

| Protocol | Port | Example Devices |
|----------|------|-----------------|
| Meitrack | 7001 | T333, T366, MVT340, MVT380 |
| Teltonika | 7002 | FMB920, FMB140, FMM130 |
| Meiligao | 7003 | GT30, GT60, VT300, VT310 |
| Megastek | 7004 | MT60, MT68, MT90 |
| Totem | 7005 | AT07, AT09 |
| Tzone | 7006 | AVL01, AVL02, AVL05 |
| Coban | 7007 | GPS102, GPS103, TK102, TK103 |
| Queclink | 7008 | GL200, GL300, GV200, GV300 |
| Fifotrack | 7009 | A300, A500, A600 |
| Suntech | 7010 | ST300, ST310, ST340, ST940 |
| TkStar | 7011 | TK905, TK915, TK905B |
| SinoTrack | 7012 | ST901, ST906, ST908 |
| Concox/GT06 | 7013 | GT06, GT06N, JM-VL, WeTrack |
| CanTrack | 7014 | Various |
| LKGPS | 7015 | LK106, LK109, LK110 |
| Carscop | 7016 | Various |
| Xexun | 7017 | TK102, TK103, XT009, XT011 |
| iStartek | 7018 | VT900, VT200, VT380 |
| XeElectech | 7019 | Various |
| VjoyCar | 7020 | TK06A, TK10, T18 |
| Eelink | 7021 | TK115, TK116, TK119, GPT18 |
| Gosafe | 7022 | G1C, G3S, G6S, G737 |
| Skypatrol | 7023 | TT8750, TT8850 |
| Xirgo | 7024 | XT2000, XT4700, XT6000 |
| Smartrack | 7025 | Various |
| ReachFar | 7026 | RF-V8, RF-V16, RF-V26 |
| iCarGPS | 7027 | Various |
| iTracGPS | 7028 | Various |
| Alematics | 7029 | Various |
| Pretrace | 7030 | Various |
| Arknav | 7031 | Various |
| Haicom | 7032 | HI-603X, HI-604X |
| CarTrackGPS | 7033 | Various |
| KingSword | 7034 | Various |
| Amwell | 7035 | Various |
| Sanav | 7036 | Various |
| Gotop | 7037 | Various |
| GlobalSat | 7038 | TR-151, TR-203, TR-206 |
| GoPass | 7039 | Various |
| Jointech | 7040 | Various |
| KeSon | 7041 | Various |
| Bofan | 7042 | PT502, PT600 |
| VSun | 7043 | Various |
| BlueIdea | 7044 | Various |
| ManPower | 7045 | Various |
| WondeProud | 7046 | Various |
| GPSMarker | 7047 | Various |
| Eview | 7048 | Various |
| Freedom | 7049 | Various |
| Topfly | 7050 | Various |
| Laipac | 7052 | S911, S911 Lola, S111 |
| Navtelecom | 7054 | SIGNAL S-2550, S-2551 |
| Galileosky | 7055 | Various |
| Ruptela | 7056 | FM-Tco4, FM-Eco4, FM-Pro4 |
| Arusnavi | 7057 | Various |
| Neomatica | 7058 | Various |
| Satellite | 7059 | Various |
| Autofon | 7060 | Various |
| ATrack | 7061 | AL1, AK1, AK11, AU5, AT5 |

## Requirements

- Python 3.8 or higher
- No external dependencies for core functionality

## Installation

```bash
# Clone the repository
git clone https://github.com/navtrack/navtrack.git
cd navtrack/python_server

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (minimal)
pip install -r requirements.txt
```

## Quick Start

### Start the Server

```bash
# Start with all protocols
python main.py

# Start with specific log level
python main.py --log-level DEBUG

# List all supported protocols
python main.py --list-protocols
```

### Connect a Device

Configure your GPS device to connect to:
- **Server**: Your server IP address
- **Port**: The port for your device protocol (see table above)

For example, for a Coban TK103 device:
- Protocol: Coban
- Port: 7007

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NAVTRACK_HOST` | `0.0.0.0` | Server bind address |
| `NAVTRACK_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |

### Command Line Arguments

```bash
python main.py --help

options:
  -h, --help            show this help message and exit
  --host HOST           Host address to bind to (default: 0.0.0.0)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level (default: INFO)
  --list-protocols      List all supported protocols and exit
```

## Integration

### Custom Message Handler

To process received GPS positions, modify the `on_message_received` callback in `main.py`:

```python
def on_message_received(message: DeviceMessage, context: ConnectionContext) -> None:
    """Handle received GPS positions."""
    
    device_id = context.device.serial_number if context.device else "unknown"
    
    # Store in database
    db.save_position(
        device_id=device_id,
        latitude=message.latitude,
        longitude=message.longitude,
        speed=message.speed,
        timestamp=message.date
    )
    
    # Send to message queue
    mq.publish('gps.positions', message.to_dict())
    
    # Check geofences
    check_geofences(device_id, message.latitude, message.longitude)
```

### Running as a Service

#### Systemd (Linux)

Create `/etc/systemd/system/navtrack-gps.service`:

```ini
[Unit]
Description=Navtrack GPS Tracking Server
After=network.target

[Service]
Type=simple
User=navtrack
WorkingDirectory=/opt/navtrack/python_server
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable navtrack-gps
sudo systemctl start navtrack-gps
```

#### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY python_server/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7001-7061

CMD ["python", "main.py"]
```

Run:

```bash
docker build -t navtrack-gps .
docker run -d -p 7001-7061:7001-7061 navtrack-gps
```

## Protocol Development

### Adding a New Protocol

1. Create a new file in `protocols/`:

```python
# protocols/mydevice.py
from ..server.protocol import BaseProtocol
from ..server.message_handler import BaseMessageHandler
from ..models.device_message import DeviceMessage

class MyDeviceProtocol(BaseProtocol):
    @property
    def port(self) -> int:
        return 7100
    
    @property
    def message_end(self) -> list:
        return [b"\r\n"]

class MyDeviceMessageHandler(BaseMessageHandler):
    def parse(self, input_data) -> DeviceMessage:
        # Parse the message
        parts = input_data.data_message.comma_split
        
        # Extract device ID
        input_data.connection_context.set_device(parts[0])
        
        # Return parsed position
        return DeviceMessage(
            latitude=float(parts[1]),
            longitude=float(parts[2]),
            speed=int(parts[3]),
            valid=True
        )
```

2. Add to `protocols/__init__.py`:

```python
from .mydevice import MyDeviceProtocol, MyDeviceMessageHandler

ALL_PROTOCOLS.append((MyDeviceProtocol, MyDeviceMessageHandler))
```

## Testing

### Testing Device Connection

You can test device connections using `telnet` or `nc`:

```bash
# Test Coban protocol
echo -e "##,imei:123456789012345,A;" | nc localhost 7007

# Should receive: LOAD
```

### Testing with Device Simulator

A device simulator is available in the original Navtrack project:

```bash
cd backend/Navtrack.Listener.DeviceSimulator
dotnet run
```

## Security Considerations

1. **Firewall**: Only expose necessary ports
2. **Rate Limiting**: Implement connection rate limiting for production
3. **Device Validation**: Add device whitelist/authentication
4. **TLS**: Consider implementing TLS for sensitive deployments

## Troubleshooting

### Device Not Connecting

1. Check firewall rules
2. Verify device is configured with correct IP and port
3. Check protocol compatibility
4. Enable DEBUG logging: `--log-level DEBUG`

### Position Not Parsed

1. Enable DEBUG logging to see raw data
2. Check if protocol matches device
3. Verify device GPS has a fix

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [Navtrack Main Project](https://github.com/navtrack/navtrack) - Full GPS tracking platform
- [Traccar](https://www.traccar.org/) - Another open-source GPS tracking platform
