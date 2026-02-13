import struct

class ByteReader:
    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.offset = 0

    def get_one(self) -> int:
        if self.offset >= len(self.buffer):
            raise IndexError("Buffer underflow")
        value = self.buffer[self.offset]
        self.offset += 1
        return value

    def get(self, count: int) -> bytes:
        if self.offset + count > len(self.buffer):
            raise IndexError("Buffer underflow")
        value = self.buffer[self.offset : self.offset + count]
        self.offset += count
        return value

    # Helper methods to match C# extensions
    # ToUInt4 -> 4 bytes to uint
    # ToSLong8 -> 8 bytes to long
    # ToSShort2 -> 2 bytes to short
    # ToUShort2 -> 2 bytes to ushort
    # ToSInt4 -> 4 bytes to int

class HexUtil:
    @staticmethod
    def convert_hex_string_to_byte_array(hex_string: str) -> bytes:
        return bytes.fromhex(hex_string)

    @staticmethod
    def convert_byte_array_to_hex_string_array(byte_array: bytes) -> list[str]:
        return [f"{b:02X}" for b in byte_array]

    @staticmethod
    def convert_byte_array_to_hex_string(byte_array: bytes) -> str:
        return byte_array.hex().upper()

class StringUtil:
    @staticmethod
    def convert_byte_array_to_string(byte_array: bytes) -> str:
        # Assuming ASCII or UTF-8 based on C# Encoding.ASCII or default
        try:
            return byte_array.decode('ascii')
        except UnicodeDecodeError:
            return byte_array.decode('utf-8', errors='ignore')

# Extension helpers
def to_uint4(b: bytes) -> int:
    return struct.unpack('>I', b)[0]

def to_slong8(b: bytes) -> int:
    return struct.unpack('>q', b)[0]

def to_ulong8(b: bytes) -> int:
    return struct.unpack('>Q', b)[0]

def to_sshort2(b: bytes) -> int:
    return struct.unpack('>h', b)[0]

def to_ushort2(b: bytes) -> int:
    return struct.unpack('>H', b)[0]

def to_ubyte1(b: bytes) -> int:
    if isinstance(b, int): return b
    return b[0]

def to_sbyte1(b: bytes) -> int:
     # signed byte
    return struct.unpack('b', b if isinstance(b, bytes) else bytes([b]))[0]

def to_sint4(b: bytes) -> int:
    return struct.unpack('>i', b)[0]

def to_boolean(b: bytes) -> bool:
    val = b[0] if isinstance(b, bytes) else b
    return val == 1
