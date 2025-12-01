"""CanTrack GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class CanTrackProtocol(TkStarProtocol):
    """CanTrack GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7014


class CanTrackMessageHandler(TkStarMessageHandler):
    """Message handler for CanTrack protocol."""
    pass
