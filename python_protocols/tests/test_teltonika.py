import unittest
from datetime import datetime
from python_protocols.helpers.byte_utils import ByteReader
from python_protocols.protocols.teltonika.teltonika_message_handler import TeltonikaMessageHandler
from python_protocols.protocols.teltonika.teltonika_protocol import TeltonikaProtocol
from python_protocols.models.device_message_entity import DeviceMessageEntity

class MockConnectionContext:
    def __init__(self):
        self.device = None

    def set_device(self, imei):
        self.device = imei

class MockNetworkStream:
    def __init__(self):
        self.buffer = b""

    def write(self, data):
        self.buffer += data

class MockDataMessage:
    def __init__(self, buffer):
        self.buffer = buffer
        self.byte_reader = ByteReader(buffer)

class MockMessageInput:
    def __init__(self, connection_context, data_message, network_stream):
        self.connection_context = connection_context
        self.data_message = data_message
        self.network_stream = network_stream

class TestTeltonikaProtocol(unittest.TestCase):
    def test_message_length(self):
        protocol = TeltonikaProtocol()
        # 0000 0000 0000 000A (length 10) ...
        # 4 zero bytes
        # 4 bytes length (e.g., 10)
        # 10 bytes data
        # 4 bytes CRC
        # Total = 4 + 4 + 10 + 4 = 22
        buffer = bytes([0, 0, 0, 0, 0, 0, 0, 10]) + bytes([0]*10) + bytes([0]*4)
        length = protocol.get_message_length(buffer, len(buffer))
        self.assertEqual(length, 22)

    def test_parse_imei(self):
        # Test that handler parses IMEI if device is not set
        handler = TeltonikaMessageHandler()
        context = MockConnectionContext()
        stream = MockNetworkStream()

        # IMEI message: 2 bytes length + 15 bytes IMEI
        # But `TeltonikaMessageHandler.ParseRange` checks `if (input.DataMessage.Bytes.Length > 16)`
        # And reads `input.DataMessage.Bytes[2..17]`
        imei_str = "123456789012345"
        buffer = bytes([0, 15]) + imei_str.encode('ascii')

        data_message = MockDataMessage(buffer)
        input_data = MockMessageInput(context, data_message, stream)

        result = handler.parse_range(input_data)

        self.assertIsNone(result)
        self.assertEqual(context.device, imei_str)
        self.assertEqual(stream.buffer, bytes([1]))

    def test_parse_data(self):
        handler = TeltonikaMessageHandler()
        context = MockConnectionContext()
        context.set_device("123456789012345")
        stream = MockNetworkStream()

        # Construct a valid packet
        # Preamble: 4 bytes (zeros)
        # Data Field Length: 4 bytes
        # Codec ID: 1 byte (0x08 for Codec8)
        # Number of Data 1: 1 byte (e.g. 1)
        # Timestamp: 8 bytes
        # Priority: 1 byte
        # Longitude: 4 bytes
        # Latitude: 4 bytes
        # Altitude: 2 bytes
        # Angle: 2 bytes
        # Satellites: 1 byte
        # Speed: 2 bytes
        # Event IO ID: 1 byte (Codec8)
        # Generation Type: 0 bytes (Codec8 doesn't have it)
        # Total IO count: 1 byte (for 1 byte IOs? No, total count usually)
        # Wait, the structure in GetPosition loop:
        # timestamp(8) + priority(1) + long(4) + lat(4) + alt(2) + angle(2) + sat(1) + speed(2) + eventID(1) + total_io_count(1)?

        # Let's recheck `GetPosition` logic for Codec8.
        # It calls `GetCodec` first to determine config.
        # `GetCodec` reads 4 preamble, 4 length, 1 codecID.

        # Inside `GetPositions`:
        # `byte noOfLocations = input.DataMessage.ByteReader.GetOne();`
        # `for ... GetPosition(...)`

        # `GetPosition`:
        # timestamp(8)
        # priority(1)
        # long(4)
        # lat(4)
        # alt(2)
        # angle(2)
        # sat(1)
        # speed(2)
        # eventId(1) (Codec8 mainEventIdLength=1)
        # DataPacketsCount? `input.DataMessage.ByteReader.Get(teltonikaCodecConfiguration.DataPacketCountBytes)`
        # Codec8 DataPacketCountBytes=1. So 1 byte for N of 1-byte IOs + N of 2-byte IOs + ...?
        # No, `MapDataPackets` reads `numberOfDataPackets`.
        # `GetNumberOfDataPackets` reads 1 byte (if dataPacketBytes=1) for count.

        # So structure for 1 location:
        # Timestamp (8)
        # Priority (1)
        # Long (4)
        # Lat (4)
        # Alt (2)
        # Angle (2)
        # Sat (1)
        # Speed (2)
        # EventID (1)
        # Global IO count (1) (DataPacketCountBytes)
        # 1-byte IO count (1) -> N * (ID(1) + Value(1))
        # 2-byte IO count (1) -> N * (ID(1) + Value(2))
        # 4-byte IO count (1) -> N * (ID(1) + Value(4))
        # 8-byte IO count (1) -> N * (ID(1) + Value(8))
        # Variable IO count (1? No, Codec8 hasVariableDataPackets=False) -> 0 bytes

        # Let's construct:
        import struct

        # Header
        preamble = bytes([0, 0, 0, 0])
        codec_id = 0x08

        # 1 location
        num_locations = 1

        # Location Data
        timestamp = 1609459200000 # 2021-01-01
        priority = 0
        longitude = 123456789 # 12.3456789
        latitude = 123456789
        altitude = 100
        angle = 0
        sat = 5
        speed = 10
        event_id = 0

        # IOs
        total_io_count = 1 # Just a placeholder byte, code reads it but ignores result?

        # 1 byte IOs
        io_1b_count = 1
        io_1b_id = 1 # Digital Input 1
        io_1b_val = 1

        # Other IO counts 0
        io_2b_count = 0
        io_4b_count = 0
        io_8b_count = 0

        loc_data = b""
        loc_data += struct.pack('>q', timestamp)
        loc_data += struct.pack('B', priority)
        loc_data += struct.pack('>i', longitude)
        loc_data += struct.pack('>i', latitude)
        loc_data += struct.pack('>h', altitude)
        loc_data += struct.pack('>h', angle)
        loc_data += struct.pack('B', sat)
        loc_data += struct.pack('>h', speed)
        loc_data += struct.pack('B', event_id)
        loc_data += struct.pack('B', total_io_count)

        loc_data += struct.pack('B', io_1b_count)
        loc_data += struct.pack('B', io_1b_id) + struct.pack('B', io_1b_val)

        loc_data += struct.pack('B', io_2b_count)
        loc_data += struct.pack('B', io_4b_count)
        loc_data += struct.pack('B', io_8b_count)

        # No variable IOs for Codec8

        # Payload
        payload = struct.pack('B', codec_id) + struct.pack('B', num_locations) + loc_data

        length = len(payload)
        buffer = preamble + struct.pack('>I', length) + payload

        data_message = MockDataMessage(buffer)
        input_data = MockMessageInput(context, data_message, stream)

        messages = handler.parse_range(input_data)

        self.assertEqual(len(messages), 1)
        msg = messages[0]
        self.assertEqual(msg.longitude, 12.3456789)
        self.assertEqual(msg.additional_data_dic['1'], 'True') # DigitalInput1

if __name__ == '__main__':
    unittest.main()
