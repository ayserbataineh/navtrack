"""GT06 GPS protocol - alias for Concox."""

from .concox import ConcoxProtocol, ConcoxMessageHandler

# GT06 is essentially the same protocol as Concox
GT06Protocol = ConcoxProtocol
GT06MessageHandler = ConcoxMessageHandler
