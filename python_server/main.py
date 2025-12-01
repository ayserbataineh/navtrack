#!/usr/bin/env python3
"""
Navtrack Python GPS Tracking Server

A standalone Python implementation supporting 60+ GPS device protocols.
Devices can connect directly to this server.

Usage:
    python main.py [--config config.yaml]
    
Configuration can be provided via:
    - Command line arguments
    - Environment variables (NAVTRACK_*)
    - YAML configuration file
"""

import asyncio
import argparse
import logging
import signal
import sys
import os
from typing import Optional

# Add package to path
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)
parent_dir = os.path.dirname(package_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import after path setup
from python_server.server.tcp_server import TCPServer
from python_server.protocols import ALL_PROTOCOLS
from python_server.models.device_message import DeviceMessage
from python_server.models.connection_context import ConnectionContext

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(numeric_level)
    
    # Set specific loggers
    logging.getLogger("server").setLevel(numeric_level)
    logging.getLogger("protocols").setLevel(numeric_level)


def on_message_received(message: DeviceMessage, context: ConnectionContext) -> None:
    """
    Callback for when a GPS message is received and parsed.
    
    This is where you would:
    - Store the position in a database
    - Forward to other systems
    - Trigger alerts based on geofences
    - etc.
    """
    device_id = context.device.serial_number if context.device else "unknown"
    
    logger.info(
        f"Position received - Device: {device_id}, "
        f"Protocol: {context.protocol.name}, "
        f"Lat: {message.latitude}, Lon: {message.longitude}, "
        f"Speed: {message.speed} km/h"
    )
    
    # Here you would typically:
    # 1. Validate the message
    # 2. Store in database
    # 3. Send to message queue
    # 4. Update real-time tracking
    
    # Example: Print full message details
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Full message: {message.to_dict()}")


async def main(
    host: str = "0.0.0.0",
    protocols: Optional[list] = None,
    log_level: str = "INFO"
) -> None:
    """
    Main entry point for the GPS tracking server.
    
    Args:
        host: Host address to bind to
        protocols: List of protocol classes to enable (None = all)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    setup_logging(log_level)
    
    logger.info("=" * 60)
    logger.info("Navtrack Python GPS Tracking Server")
    logger.info("=" * 60)
    
    # Create server
    server = TCPServer()
    
    # Register message callback
    server.on_message(on_message_received)
    
    # Register protocols
    protocols_to_register = protocols or ALL_PROTOCOLS
    registered_count = 0
    
    for protocol_class, handler_class in protocols_to_register:
        try:
            protocol = protocol_class()
            handler = handler_class()
            server.register_protocol(protocol, handler)
            registered_count += 1
        except Exception as e:
            logger.error(f"Failed to register {protocol_class.__name__}: {e}")
    
    logger.info(f"Registered {registered_count} protocols")
    logger.info("-" * 60)
    
    # Setup graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        logger.info("Shutdown signal received")
        shutdown_event.set()
    
    # Register signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    # Start server
    try:
        logger.info(f"Starting server on {host}")
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 60)
        
        # Run server and wait for shutdown
        server_task = asyncio.create_task(server.start(host))
        shutdown_task = asyncio.create_task(shutdown_event.wait())
        
        done, pending = await asyncio.wait(
            [server_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.stop()
        logger.info("Server stopped")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Navtrack Python GPS Tracking Server"
    )
    
    parser.add_argument(
        "--host",
        default=os.environ.get("NAVTRACK_HOST", "0.0.0.0"),
        help="Host address to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--log-level",
        default=os.environ.get("NAVTRACK_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--list-protocols",
        action="store_true",
        help="List all supported protocols and exit"
    )
    
    return parser.parse_args()


def list_protocols() -> None:
    """Print list of all supported protocols."""
    print("\nSupported GPS Protocols:")
    print("-" * 60)
    print(f"{'Protocol':<30} {'Port':<10} {'Devices'}")
    print("-" * 60)
    
    for protocol_class, _ in sorted(ALL_PROTOCOLS, key=lambda x: x[0]().port):
        protocol = protocol_class()
        print(f"{protocol.name:<30} {protocol.port:<10}")
    
    print("-" * 60)
    print(f"Total: {len(ALL_PROTOCOLS)} protocols")
    print()


if __name__ == "__main__":
    args = parse_args()
    
    if args.list_protocols:
        list_protocols()
        sys.exit(0)
    
    try:
        asyncio.run(main(
            host=args.host,
            log_level=args.log_level
        ))
    except KeyboardInterrupt:
        print("\nShutdown complete")
