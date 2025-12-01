"""SinoTrack GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class SinoTrackProtocol(TkStarProtocol):
    """SinoTrack GPS tracker protocol (ST901, ST906, ST908, etc.)."""
    
    @property
    def port(self) -> int:
        return 7012


class SinoTrackMessageHandler(TkStarMessageHandler):
    """Message handler for SinoTrack protocol."""
    pass
