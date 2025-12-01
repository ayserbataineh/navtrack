"""
Protocol Definitions Module

This module contains all GPS tracking protocol definitions extracted from
the Navtrack platform. Each protocol includes:
- Port number
- Message start/end patterns
- Message delimiter
- Custom message length logic (if applicable)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Callable
from enum import Enum


class MessagePriority(Enum):
    """Message priority levels."""
    NORMAL = "Normal"
    HIGH = "High"
    EMERGENCY = "Emergency"


@dataclass
class Protocol:
    """
    Base protocol definition class.
    
    Attributes:
        name: Protocol name
        port: TCP port number for the protocol
        message_start: Bytes that indicate the start of a message
        message_end: Bytes that indicate the end of a message
        split_message_by: Character to split messages by
        has_custom_length: Whether the protocol has custom message length logic
        parent_protocol: Name of parent protocol if this extends another
        description: Human-readable description of the protocol
        manufacturer: Device manufacturer
        supported_devices: List of supported device models
    """
    name: str
    port: int
    message_start: Optional[bytes] = None
    message_end: Optional[List[bytes]] = None
    split_message_by: Optional[str] = None
    has_custom_length: bool = False
    parent_protocol: Optional[str] = None
    description: str = ""
    manufacturer: str = ""
    supported_devices: List[str] = None
    
    def __post_init__(self):
        if self.supported_devices is None:
            self.supported_devices = []
    
    def get_message_length(self, buffer: bytes, bytes_read_count: int) -> Optional[int]:
        """
        Get the expected message length from the buffer.
        Override this method for protocols with custom message length logic.
        
        Args:
            buffer: The byte buffer containing the incoming data
            bytes_read_count: Number of bytes read so far
            
        Returns:
            Expected message length or None if not determinable
        """
        return None
    
    def is_message_complete(self, buffer: bytes) -> bool:
        """
        Check if the message in the buffer is complete.
        
        Args:
            buffer: The byte buffer containing the incoming data
            
        Returns:
            True if message is complete, False otherwise
        """
        if self.message_end:
            for end_pattern in self.message_end:
                if buffer.endswith(end_pattern):
                    return True
            return False
        return True
    
    def to_dict(self) -> dict:
        """Convert the protocol to a dictionary."""
        return {
            "name": self.name,
            "port": self.port,
            "message_start": self.message_start.hex() if self.message_start else None,
            "message_end": [e.hex() for e in self.message_end] if self.message_end else None,
            "split_message_by": self.split_message_by,
            "has_custom_length": self.has_custom_length,
            "parent_protocol": self.parent_protocol,
            "description": self.description,
            "manufacturer": self.manufacturer,
            "supported_devices": self.supported_devices,
        }


# =============================================================================
# Protocol Definitions
# =============================================================================

class MeitrackProtocol(Protocol):
    """Meitrack GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Meitrack",
            port=7001,
            message_start=bytes([0x24, 0x24]),  # $$
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Meitrack GPS tracking protocol",
            manufacturer="Meitrack",
            supported_devices=["MVT340", "MVT380", "MT90", "T1", "T3", "T333", "TC68L"]
        )


class TeltonikaProtocol(Protocol):
    """Teltonika GPS Tracker Protocol with custom message length logic"""
    def __init__(self):
        super().__init__(
            name="Teltonika",
            port=7002,
            has_custom_length=True,
            description="Teltonika GPS tracking protocol supporting Codec 8, 8 Extended, and 16",
            manufacturer="Teltonika",
            supported_devices=["FMB920", "FMB140", "FMB120", "FMC130", "FMU130", "FM3001", "FMT100"]
        )
    
    def get_message_length(self, buffer: bytes, bytes_read_count: int) -> Optional[int]:
        """
        Teltonika message length calculation.
        
        Message format:
        - 4 bytes: Preamble (0x00 0x00 0x00 0x00)
        - 4 bytes: Data field length
        - N bytes: Data
        - 4 bytes: CRC
        """
        if bytes_read_count > 7 and buffer[0:4] == bytes([0, 0, 0, 0]):
            prefix_length = 4
            data_field_length = 4
            data_length = int.from_bytes(buffer[4:8], byteorder='big')
            crc_length = 4
            total_length = prefix_length + data_field_length + data_length + crc_length
            return total_length
        return None


class MeiligaoProtocol(Protocol):
    """Meiligao GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Meiligao",
            port=7003,
            message_start=bytes([0x24, 0x24]),  # $$
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Meiligao GPS tracking protocol",
            manufacturer="Meiligao"
        )


class MegastekProtocol(Protocol):
    """Megastek GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Megastek",
            port=7004,
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Megastek GPS tracking protocol",
            manufacturer="Megastek"
        )


class TotemProtocol(Protocol):
    """Totem GPS Tracker Protocol with custom message length logic"""
    def __init__(self):
        super().__init__(
            name="Totem",
            port=7005,
            message_start=bytes([0x24, 0x24]),  # $$
            has_custom_length=True,
            description="Totem GPS tracking protocol",
            manufacturer="Totem"
        )
    
    def get_message_length(self, buffer: bytes, bytes_read_count: int) -> Optional[int]:
        """
        Totem message length calculation.
        
        Message format:
        - 2 bytes: Header ($$)
        - 4 bytes: Length (ASCII digits)
        - N bytes: Data
        """
        if len(buffer) >= 6:
            header_index = buffer.find(self.message_start)
            if header_index >= 0:
                length_start = header_index + 2
                length_end = length_start + 4
                try:
                    length = int(buffer[length_start:length_end].decode('ascii'))
                    return length
                except (ValueError, UnicodeDecodeError):
                    pass
        return None


class TzoneProtocol(Protocol):
    """Tzone GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Tzone",
            port=7006,
            message_start=bytes([0x24, 0x24]),  # $$
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Tzone GPS tracking protocol",
            manufacturer="Tzone"
        )


class CobanProtocol(Protocol):
    """Coban GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Coban",
            port=7007,
            message_end=[bytes([0x3B])],  # ;
            description="Coban GPS103/GPS303 tracking protocol",
            manufacturer="Coban",
            supported_devices=["GPS103", "GPS303", "TK103", "TK303"]
        )


class QueclinkProtocol(Protocol):
    """Queclink GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Queclink",
            port=7008,
            message_end=[bytes([0x24])],  # $
            description="Queclink GPS tracking protocol",
            manufacturer="Queclink",
            supported_devices=["GL300", "GL500", "GL505", "GV55", "GV65", "GV300"]
        )


class FifotrackProtocol(Protocol):
    """Fifotrack GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Fifotrack",
            port=7009,
            message_start=bytes([0x24, 0x24]),  # $$
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Fifotrack GPS tracking protocol",
            manufacturer="Fifotrack"
        )


class SuntechProtocol(Protocol):
    """Suntech GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Suntech",
            port=7010,
            split_message_by=";",
            description="Suntech GPS tracking protocol",
            manufacturer="Suntech"
        )


class TkStarProtocol(Protocol):
    """TkStar GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="TkStar",
            port=7011,
            message_start=bytes([0x2A]),  # *
            message_end=[bytes([0x23])],  # #
            description="TkStar GPS tracking protocol",
            manufacturer="TkStar"
        )


class SinoTrackProtocol(TkStarProtocol):
    """SinoTrack GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "SinoTrack"
        self.port = 7012
        self.parent_protocol = "TkStar"
        self.description = "SinoTrack GPS tracking protocol"
        self.manufacturer = "SinoTrack"
        self.supported_devices = ["ST901", "ST906"]


class ConcoxProtocol(Protocol):
    """Concox GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Concox",
            port=7013,
            message_start=bytes([0x78, 0x78]),
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="Concox GPS tracking protocol",
            manufacturer="Concox",
            supported_devices=["GT06", "GT06N", "JM01", "JM08", "GK309"]
        )


class CanTrackProtocol(TkStarProtocol):
    """CanTrack GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "CanTrack"
        self.port = 7014
        self.parent_protocol = "TkStar"
        self.description = "CanTrack GPS tracking protocol"
        self.manufacturer = "CanTrack"


class LKGPSProtocol(TkStarProtocol):
    """LKGPS GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "LKGPS"
        self.port = 7015
        self.parent_protocol = "TkStar"
        self.description = "LKGPS GPS tracking protocol"
        self.manufacturer = "LKGPS"


class CarscopProtocol(TkStarProtocol):
    """Carscop GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "Carscop"
        self.port = 7016
        self.parent_protocol = "TkStar"
        self.message_end = [bytes([0x23])]  # #
        self.description = "Carscop GPS tracking protocol"
        self.manufacturer = "Carscop"


class XexunProtocol(Protocol):
    """Xexun GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Xexun",
            port=7017,
            description="Xexun GPS tracking protocol",
            manufacturer="Xexun"
        )


class iStartekProtocol(TkStarProtocol):
    """iStartek GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "iStartek"
        self.port = 7018
        self.parent_protocol = "TkStar"
        self.description = "iStartek GPS tracking protocol"
        self.manufacturer = "iStartek"


class XeElectechProtocol(Protocol):
    """XeElectech GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="XeElectech",
            port=7019,
            description="XeElectech GPS tracking protocol",
            manufacturer="XeElectech"
        )


class VjoyCarProtocol(TkStarProtocol):
    """VjoyCar GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "VjoyCar"
        self.port = 7020
        self.parent_protocol = "TkStar"
        self.description = "VjoyCar GPS tracking protocol"
        self.manufacturer = "VjoyCar"


class EelinkProtocol(Protocol):
    """Eelink GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Eelink",
            port=7021,
            message_start=bytes([0x67, 0x67]),
            description="Eelink GPS tracking protocol",
            manufacturer="Eelink"
        )


class GosafeProtocol(Protocol):
    """Gosafe GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Gosafe",
            port=7022,
            message_start=bytes([0x2A]),  # *
            message_end=[bytes([0x23])],  # #
            description="Gosafe GPS tracking protocol",
            manufacturer="Gosafe"
        )


class SkypatrolProtocol(GosafeProtocol):
    """Skypatrol GPS Tracker Protocol (extends Gosafe)"""
    def __init__(self):
        super().__init__()
        self.name = "Skypatrol"
        self.port = 7023
        self.parent_protocol = "Gosafe"
        self.description = "Skypatrol GPS tracking protocol"
        self.manufacturer = "Skypatrol"


class XirgoProtocol(Protocol):
    """Xirgo GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Xirgo",
            port=7024,
            message_start=bytes([0x24, 0x24]),  # $$
            message_end=[bytes([0x23, 0x23])],  # ##
            description="Xirgo GPS tracking protocol",
            manufacturer="Xirgo"
        )


class SmartrackProtocol(Protocol):
    """Smartrack GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Smartrack",
            port=7025,
            description="Smartrack GPS tracking protocol",
            manufacturer="Smartrack"
        )


class ReachFarProtocol(Protocol):
    """ReachFar GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="ReachFar",
            port=7026,
            description="ReachFar GPS tracking protocol",
            manufacturer="ReachFar"
        )


class iCarGPSProtocol(TkStarProtocol):
    """iCarGPS GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "iCarGPS"
        self.port = 7027
        self.parent_protocol = "TkStar"
        self.description = "iCarGPS GPS tracking protocol"
        self.manufacturer = "iCarGPS"


class iTracGPSProtocol(TkStarProtocol):
    """iTracGPS GPS Tracker Protocol (extends TkStar)"""
    def __init__(self):
        super().__init__()
        self.name = "iTracGPS"
        self.port = 7028
        self.parent_protocol = "TkStar"
        self.description = "iTracGPS GPS tracking protocol"
        self.manufacturer = "iTracGPS"


class AlematicsProtocol(Protocol):
    """Alematics GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Alematics",
            port=7029,
            message_start=bytes([0x24]),  # $
            description="Alematics GPS tracking protocol",
            manufacturer="Alematics"
        )


class PretraceProtocol(Protocol):
    """Pretrace GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Pretrace",
            port=7030,
            message_start=bytes([0x28]),  # (
            message_end=[bytes([0x29])],  # )
            description="Pretrace GPS tracking protocol",
            manufacturer="Pretrace"
        )


class ArknavProtocol(Protocol):
    """Arknav GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Arknav",
            port=7031,
            description="Arknav GPS tracking protocol",
            manufacturer="Arknav"
        )


class HaicomProtocol(Protocol):
    """Haicom GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Haicom",
            port=7032,
            description="Haicom GPS tracking protocol",
            manufacturer="Haicom"
        )


class CarTrackGPSProtocol(Protocol):
    """CarTrackGPS GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="CarTrackGPS",
            port=7033,
            description="CarTrackGPS GPS tracking protocol",
            manufacturer="CarTrackGPS"
        )


class KingSwordProtocol(Protocol):
    """KingSword GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="KingSword",
            port=7034,
            description="KingSword GPS tracking protocol",
            manufacturer="KingSword"
        )


class AmwellProtocol(Protocol):
    """Amwell GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Amwell",
            port=7035,
            description="Amwell GPS tracking protocol",
            manufacturer="Amwell"
        )


class SanavProtocol(Protocol):
    """Sanav GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Sanav",
            port=7036,
            description="Sanav GPS tracking protocol",
            manufacturer="Sanav"
        )


class GotopProtocol(Protocol):
    """Gotop GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Gotop",
            port=7037,
            description="Gotop GPS tracking protocol",
            manufacturer="Gotop"
        )


class GlobalSatProtocol(Protocol):
    """GlobalSat GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="GlobalSat",
            port=7038,
            message_start=bytes([0x24]),  # $
            description="GlobalSat GPS tracking protocol",
            manufacturer="GlobalSat"
        )


class GoPassProtocol(Protocol):
    """GoPass GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="GoPass",
            port=7039,
            description="GoPass GPS tracking protocol",
            manufacturer="GoPass"
        )


class JointechProtocol(Protocol):
    """Jointech GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Jointech",
            port=7040,
            description="Jointech GPS tracking protocol",
            manufacturer="Jointech"
        )


class KeSonProtocol(Protocol):
    """KeSon GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="KeSon",
            port=7041,
            message_start=bytes([0x23]),  # #
            message_end=[bytes([0x3B])],  # ;
            description="KeSon GPS tracking protocol",
            manufacturer="KeSon"
        )


class BofanProtocol(Protocol):
    """Bofan GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Bofan",
            port=7042,
            description="Bofan GPS tracking protocol",
            manufacturer="Bofan"
        )


class VSunProtocol(Protocol):
    """VSun GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="VSun",
            port=7043,
            message_end=[bytes([0x0D, 0x0A])],  # \r\n
            description="VSun GPS tracking protocol",
            manufacturer="VSun"
        )


class BlueIdeaProtocol(BofanProtocol):
    """BlueIdea GPS Tracker Protocol (extends Bofan)"""
    def __init__(self):
        super().__init__()
        self.name = "BlueIdea"
        self.port = 7044
        self.parent_protocol = "Bofan"
        self.description = "BlueIdea GPS tracking protocol"
        self.manufacturer = "BlueIdea"


class ManPowerProtocol(Protocol):
    """ManPower GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="ManPower",
            port=7045,
            description="ManPower GPS tracking protocol",
            manufacturer="ManPower"
        )


class WondeProudProtocol(Protocol):
    """WondeProud GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="WondeProud",
            port=7046,
            description="WondeProud GPS tracking protocol",
            manufacturer="WondeProud"
        )


class GPSMarkerProtocol(Protocol):
    """GPSMarker GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="GPSMarker",
            port=7047,
            message_start=bytes([0x24]),  # $
            message_end=[bytes([0x23])],  # #
            description="GPSMarker GPS tracking protocol",
            manufacturer="GPSMarker"
        )


class EviewProtocol(Protocol):
    """Eview GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Eview",
            port=7048,
            message_start=bytes([0x21]),  # !
            message_end=[bytes([0x3B])],  # ;
            description="Eview GPS tracking protocol",
            manufacturer="Eview"
        )


class FreedomProtocol(Protocol):
    """Freedom GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Freedom",
            port=7049,
            description="Freedom GPS tracking protocol",
            manufacturer="Freedom"
        )


class TopflyProtocol(Protocol):
    """Topfly GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Topfly",
            port=7050,
            message_start=bytes([0x23, 0x23]),  # ##
            description="Topfly GPS tracking protocol",
            manufacturer="Topfly"
        )


class ErmProtocol(Protocol):
    """StarLink/ERM GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="ERM",
            port=7051,
            description="StarLink/ERM GPS tracking protocol",
            manufacturer="StarLink"
        )


class LaipacProtocol(Protocol):
    """Laipac GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Laipac",
            port=7052,
            description="Laipac GPS tracking protocol",
            manufacturer="Laipac"
        )


class NavtelecomProtocol(Protocol):
    """Navtelecom GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Navtelecom",
            port=7054,
            description="Navtelecom GPS tracking protocol",
            manufacturer="Navtelecom"
        )


class GalileoskyProtocol(Protocol):
    """Galileosky GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Galileosky",
            port=7055,
            description="Galileosky GPS tracking protocol",
            manufacturer="Galileosky"
        )


class RuptelaProtocol(Protocol):
    """Ruptela GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Ruptela",
            port=7056,
            description="Ruptela GPS tracking protocol",
            manufacturer="Ruptela"
        )


class ArusnaviProtocol(Protocol):
    """Arusnavi GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Arusnavi",
            port=7057,
            description="Arusnavi GPS tracking protocol",
            manufacturer="Arusnavi"
        )


class NeomaticaProtocol(Protocol):
    """Neomatica GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Neomatica",
            port=7058,
            description="Neomatica GPS tracking protocol",
            manufacturer="Neomatica"
        )


class SatelliteProtocol(Protocol):
    """Satellite GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Satellite",
            port=7059,
            description="Satellite GPS tracking protocol",
            manufacturer="Satellite"
        )


class AutofonProtocol(Protocol):
    """Autofon GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="Autofon",
            port=7060,
            description="Autofon GPS tracking protocol",
            manufacturer="Autofon"
        )


class ATrackProtocol(Protocol):
    """ATrack GPS Tracker Protocol"""
    def __init__(self):
        super().__init__(
            name="ATrack",
            port=7061,
            description="ATrack GPS tracking protocol supporting binary and text messages",
            manufacturer="ATrack"
        )


# =============================================================================
# Protocol Registry
# =============================================================================

# Registry of all available protocols
_PROTOCOL_REGISTRY: Dict[str, Protocol] = {}

def _register_protocols():
    """Register all protocol classes."""
    protocol_classes = [
        MeitrackProtocol,
        TeltonikaProtocol,
        MeiligaoProtocol,
        MegastekProtocol,
        TotemProtocol,
        TzoneProtocol,
        CobanProtocol,
        QueclinkProtocol,
        FifotrackProtocol,
        SuntechProtocol,
        TkStarProtocol,
        SinoTrackProtocol,
        ConcoxProtocol,
        CanTrackProtocol,
        LKGPSProtocol,
        CarscopProtocol,
        XexunProtocol,
        iStartekProtocol,
        XeElectechProtocol,
        VjoyCarProtocol,
        EelinkProtocol,
        GosafeProtocol,
        SkypatrolProtocol,
        XirgoProtocol,
        SmartrackProtocol,
        ReachFarProtocol,
        iCarGPSProtocol,
        iTracGPSProtocol,
        AlematicsProtocol,
        PretraceProtocol,
        ArknavProtocol,
        HaicomProtocol,
        CarTrackGPSProtocol,
        KingSwordProtocol,
        AmwellProtocol,
        SanavProtocol,
        GotopProtocol,
        GlobalSatProtocol,
        GoPassProtocol,
        JointechProtocol,
        KeSonProtocol,
        BofanProtocol,
        VSunProtocol,
        BlueIdeaProtocol,
        ManPowerProtocol,
        WondeProudProtocol,
        GPSMarkerProtocol,
        EviewProtocol,
        FreedomProtocol,
        TopflyProtocol,
        ErmProtocol,
        LaipacProtocol,
        NavtelecomProtocol,
        GalileoskyProtocol,
        RuptelaProtocol,
        ArusnaviProtocol,
        NeomaticaProtocol,
        SatelliteProtocol,
        AutofonProtocol,
        ATrackProtocol,
    ]
    
    for protocol_class in protocol_classes:
        protocol = protocol_class()
        _PROTOCOL_REGISTRY[protocol.name.lower()] = protocol


def get_all_protocols() -> List[Protocol]:
    """
    Get all registered protocols.
    
    Returns:
        List of all available Protocol instances
    """
    if not _PROTOCOL_REGISTRY:
        _register_protocols()
    return list(_PROTOCOL_REGISTRY.values())


def get_protocol(name: str) -> Optional[Protocol]:
    """
    Get a protocol by name.
    
    Args:
        name: Protocol name (case-insensitive)
        
    Returns:
        Protocol instance or None if not found
    """
    if not _PROTOCOL_REGISTRY:
        _register_protocols()
    return _PROTOCOL_REGISTRY.get(name.lower())


def get_protocol_by_port(port: int) -> Optional[Protocol]:
    """
    Get a protocol by its port number.
    
    Args:
        port: TCP port number
        
    Returns:
        Protocol instance or None if not found
    """
    if not _PROTOCOL_REGISTRY:
        _register_protocols()
    for protocol in _PROTOCOL_REGISTRY.values():
        if protocol.port == port:
            return protocol
    return None
