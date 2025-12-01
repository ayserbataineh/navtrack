"""iCarGPS GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class iCarGPSProtocol(TkStarProtocol):
    """iCarGPS GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7027


class iCarGPSMessageHandler(TkStarMessageHandler):
    """Message handler for iCarGPS protocol."""
    pass
