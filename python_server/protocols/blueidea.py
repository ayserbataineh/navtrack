"""BlueIdea GPS protocol - extends Bofan."""

from .bofan import BofanProtocol, BofanMessageHandler


class BlueIdeaProtocol(BofanProtocol):
    """BlueIdea GPS tracker protocol."""
    
    @property
    def port(self) -> int:
        return 7044


class BlueIdeaMessageHandler(BofanMessageHandler):
    """Message handler for BlueIdea protocol."""
    pass
