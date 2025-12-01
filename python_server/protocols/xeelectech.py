"""XeElectech GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class XeElectechProtocol(TkStarProtocol):
    """XeElectech GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7019


class XeElectechMessageHandler(TkStarMessageHandler):
    """Message handler for XeElectech protocol."""
    pass
