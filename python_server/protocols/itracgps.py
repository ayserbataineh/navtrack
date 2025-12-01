"""iTracGPS GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class iTracGPSProtocol(TkStarProtocol):
    """iTracGPS GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7028


class iTracGPSMessageHandler(TkStarMessageHandler):
    """Message handler for iTracGPS protocol."""
    pass
