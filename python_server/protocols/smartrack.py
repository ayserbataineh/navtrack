"""Smartrack GPS protocol - extends VjoyCar."""

from .vjoycar import VjoyCarProtocol, VjoyCarMessageHandler


class SmartrackProtocol(VjoyCarProtocol):
    """Smartrack GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7025


class SmartrackMessageHandler(VjoyCarMessageHandler):
    """Message handler for Smartrack protocol."""
    pass
