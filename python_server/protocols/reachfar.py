"""ReachFar GPS protocol - extends TkStar."""

from .tkstar import TkStarProtocol, TkStarMessageHandler


class ReachFarProtocol(TkStarProtocol):
    """ReachFar GPS tracker protocol (RF-V8, RF-V16, RF-V26, etc.)."""
    
    @property
    def port(self) -> int:
        return 7026


class ReachFarMessageHandler(TkStarMessageHandler):
    """Message handler for ReachFar protocol."""
    pass
