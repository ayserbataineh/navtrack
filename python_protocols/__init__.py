"""
Navtrack GPS Tracking Protocols - Python Implementation

This module provides Python implementations of GPS tracking device protocols
extracted from the Navtrack platform.

The protocols module contains:
- Protocol definitions (ports, message start/end patterns)
- Message parsing utilities
- Device message data structures

Supported Protocols:
- ATrack
- Alematics
- Amwell
- Arknav
- Arusnavi
- Autofon
- BlueIdea
- Bofan
- CanTrack
- CarTrackGPS
- Carscop
- Coban
- Concox
- Eelink
- Eview
- Fifotrack
- Freedom
- GPSMarker
- Galileosky
- GlobalSat
- GoPass
- Gosafe
- Gotop
- Haicom
- Jointech
- KeSon
- KingSword
- LKGPS
- Laipac
- ManPower
- Megastek
- Meiligao
- Meitrack
- Navtelecom
- Neomatica
- Pretrace
- Queclink
- ReachFar
- Ruptela
- Sanav
- Satellite
- SinoTrack
- Skypatrol
- Smartrack
- StarLink/ERM
- Suntech
- Teltonika
- TkStar
- Topfly
- Totem
- Tzone
- VSun
- VjoyCar
- WondeProud
- XeElectech
- Xexun
- Xirgo
- iCarGPS
- iStartek
- iTracGPS

Usage:
    from python_protocols import protocols, DeviceMessage, Protocol

    # Get all available protocols
    all_protocols = protocols.get_all_protocols()

    # Get a specific protocol
    teltonika = protocols.get_protocol("Teltonika")

    # Parse a message (example)
    from python_protocols.protocols.teltonika import TeltonikaMessageHandler
    handler = TeltonikaMessageHandler()
    messages = handler.parse(raw_data)
"""

from .protocols import get_all_protocols, get_protocol, Protocol
from .device_message import DeviceMessage

__version__ = "1.0.0"
__all__ = [
    "get_all_protocols",
    "get_protocol",
    "Protocol",
    "DeviceMessage",
]
