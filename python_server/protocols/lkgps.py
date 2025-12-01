"""LKGPS GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class LKGPSProtocol(TkStarProtocol):
    """LKGPS GPS tracker protocol (LK106, LK109, LK110, etc.)."""
    
    @property
    def port(self) -> int:
        return 7015


class LKGPSMessageHandler(TkStarMessageHandler):
    """Message handler for LKGPS protocol."""
    pass
