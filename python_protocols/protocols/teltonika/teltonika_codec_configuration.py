from typing import Dict, Optional
from .teltonika_codec import TeltonikaCodec

class TeltonikaCodecConfiguration:
    def __init__(self, main_event_id_length: int, has_generation_type: bool,
                 data_packet_count_bytes: int, data_packet_bytes: int,
                 data_packet_id_bytes: int, has_variable_data_packets: bool):
        self.main_event_id_length = main_event_id_length
        self.has_generation_type = has_generation_type
        self.data_packet_count_bytes = data_packet_count_bytes
        self.data_packet_bytes = data_packet_bytes
        self.data_packet_id_bytes = data_packet_id_bytes
        self.has_variable_data_packets = has_variable_data_packets

    @staticmethod
    def get_all() -> Dict[TeltonikaCodec, 'TeltonikaCodecConfiguration']:
        return {
            TeltonikaCodec.Codec8: TeltonikaCodecConfiguration(1, False, 1, 1, 1, False),
            TeltonikaCodec.Codec8Extended: TeltonikaCodecConfiguration(2, False, 2, 2, 2, True),
            TeltonikaCodec.Codec16: TeltonikaCodecConfiguration(2, True, 1, 1, 2, False)
        }
