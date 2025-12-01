from typing import Optional
from python_protocols.server.base_protocol import BaseProtocol
from python_protocols.helpers.byte_utils import to_uint4

class TeltonikaProtocol(BaseProtocol):
    @property
    def port(self) -> int:
        return 7002

    def get_message_length(self, buffer: bytes, bytes_read_count: int) -> Optional[int]:
        if bytes_read_count > 7 and buffer[0] == 0 and buffer[1] == 0 and buffer[2] == 0 and buffer[3] == 0:
            prefix_length = 4
            data_field_length = 4
            # Python slicing is exclusive at the end, C# range 4..8 means index 4,5,6,7
            data_length = to_uint4(buffer[4:8])
            crc_length = 4

            total_length = prefix_length + data_field_length + int(data_length) + crc_length
            return total_length

        return super().get_message_length(buffer, bytes_read_count)
