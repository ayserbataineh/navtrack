"""Carscop GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class CarscopProtocol(TkStarProtocol):
    """Carscop GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7016


class CarscopMessageHandler(TkStarMessageHandler):
    """Message handler for Carscop protocol."""
    pass
