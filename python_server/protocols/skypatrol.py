"""Skypatrol GPS protocol - extends Gosafe."""

from .gosafe import GosafeProtocol, GosafeMessageHandler


class SkypatrolProtocol(GosafeProtocol):
    """Skypatrol GPS tracker protocol (TT8750, TT8850, etc.)."""
    
    @property
    def port(self) -> int:
        return 7023


class SkypatrolMessageHandler(GosafeMessageHandler):
    """Message handler for Skypatrol protocol."""
    pass
