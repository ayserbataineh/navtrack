from typing import List, Optional, Any, Dict
from datetime import datetime, timedelta

from python_protocols.server.base_protocol import BaseMessageHandler, MessageInput
from python_protocols.models.device_message_entity import DeviceMessageEntity
from python_protocols.helpers.byte_utils import (
    ByteReader, HexUtil, StringUtil,
    to_uint4, to_slong8, to_sshort2, to_ushort2, to_ubyte1, to_sbyte1, to_sint4, to_boolean, to_ulong8
)

from .teltonika_codec import TeltonikaCodec
from .teltonika_codec_configuration import TeltonikaCodecConfiguration
from .teltonika_data_ids import TeltonikaDataIds

class TeltonikaMessageHandler(BaseMessageHandler):
    def parse_range(self, input_data: MessageInput) -> Optional[List[DeviceMessageEntity]]:
        # Assuming input_data.connection_context is an object that has a 'device' attribute
        # and a 'set_device' method.
        # This part depends on how ConnectionContext is implemented in Python, which we haven't fully defined.
        # For now, I'll mock the behavior or assume it exists.

        if not getattr(input_data.connection_context, 'device', None):
            if len(input_data.data_message.buffer) > 16: # buffer in python is bytes
                 # C# range 2..17 -> Python 2:17 (15 chars)
                imei_bytes = input_data.data_message.buffer[2:17]
                imei = StringUtil.convert_byte_array_to_string(imei_bytes)

                input_data.connection_context.set_device(imei)

                input_data.network_stream.write(bytes([1]))

            return None

        positions = self.get_positions(input_data)

        if positions:
            reply = f"{len(positions):08X}"
            input_data.network_stream.write(HexUtil.convert_hex_string_to_byte_array(reply))

        return positions

    def get_positions(self, input_data: MessageInput) -> List[DeviceMessageEntity]:
        messages = []

        codec_configuration = self.get_codec(input_data)

        if codec_configuration is None:
            return []

        # ByteReader needs to be instantiated with the buffer
        # Assuming input_data.data_message has a byte_reader or buffer
        # In the C# code it seems input.DataMessage has a ByteReader or Bytes.
        # I'll assume input_data.data_message is an object that holds the buffer and maybe we create a reader from it
        # or it has a reader.
        # Let's assume input_data.data_message is a wrapper that we need to adapt.
        # For this port, I'll create a ByteReader from the buffer.

        # But wait, in C#, ByteReader seems stateful (cursor moves).
        # If I create a new ByteReader here, it needs to start where the previous one left off?
        # In GetPositions, it calls GetCodec which reads from the reader.
        # So I should pass the reader around.

        # Let's verify how `input.DataMessage` works in C#.
        # It seems `input.DataMessage` has `ByteReader`.

        reader = input_data.data_message.byte_reader

        no_of_locations = reader.get_one()

        for _ in range(no_of_locations):
            device_message = self.get_position(input_data, codec_configuration, reader)
            messages.append(device_message)

        return messages

    def get_codec(self, input_data: MessageInput) -> Optional[TeltonikaCodecConfiguration]:
        codecs = [c.value for c in TeltonikaCodec]

        reader = input_data.data_message.byte_reader

        preamble = reader.get(4)
        length = to_uint4(reader.get(4))
        codec_id = reader.get_one()

        if codec_id in codecs:
            codec = TeltonikaCodec(codec_id)
            return TeltonikaCodecConfiguration.get_all()[codec]

        return None

    def get_position(self, input_data: MessageInput,
                     teltonika_codec_configuration: TeltonikaCodecConfiguration,
                     reader: ByteReader) -> DeviceMessageEntity:

        device_message = DeviceMessageEntity()
        device_message.additional_data_dic = {}

        timestamp_ms = to_slong8(reader.get(8))
        # UnixEpoch is 1970-01-01
        device_message.date = datetime(1970, 1, 1) + timedelta(milliseconds=timestamp_ms)

        priority = reader.get_one()

        if priority == 1:
            device_message.message_priority = "High" # Enum
        elif priority == 2:
            device_message.message_priority = "Emergency" # Enum
        else:
            device_message.message_priority = None

        device_message.longitude = self.get_coordinate(reader.get(4))
        device_message.latitude = self.get_coordinate(reader.get(4))
        device_message.altitude = to_sshort2(reader.get(2))
        device_message.heading = to_sshort2(reader.get(2))
        device_message.satellites = reader.get_one()
        device_message.speed = to_sshort2(reader.get(2))

        if teltonika_codec_configuration.main_event_id_length == 2:
            event_id = to_ushort2(reader.get(2))
        else:
            event_id = to_ubyte1(reader.get(1))

        device_message.additional_data_dic[str(TeltonikaDataIds.EventId)] = str(event_id)

        if teltonika_codec_configuration.has_generation_type:
            generation_type = reader.get_one() # Unused in C# code

        data_packets_count_bytes = reader.get(teltonika_codec_configuration.data_packet_count_bytes)
        # The C# code reads these bytes but doesn't seem to use them immediately,
        # or maybe `dataPacketsCount` variable is unused?
        # Ah, looking at C# code: `byte[] dataPacketsCount = input.DataMessage.ByteReader.Get(...)`
        # It is not used.

        self.map_data_packets(device_message, reader, teltonika_codec_configuration, 1)
        self.map_data_packets(device_message, reader, teltonika_codec_configuration, 2)
        self.map_data_packets(device_message, reader, teltonika_codec_configuration, 4)
        self.map_data_packets(device_message, reader, teltonika_codec_configuration, 8)
        self.map_data_packets(device_message, reader, teltonika_codec_configuration) # variable

        return device_message

    def get_coordinate(self, coordinate: bytes) -> float:
        converted_coordinate = to_sint4(coordinate)
        # In Python, we don't need to manually handle binary string for sign if we unpacked as signed int
        # However, C# `ToSInt4` does `BitConverter.ToInt32(bytes.Reverse().ToArray(), 0)` (assuming big-endian if reversed or just big-endian).
        # But wait, the C# code does manual sign check?
        # `string binary = Convert.ToString(coordinate[0], 2).PadLeft(8, '0');`
        # `bool isNegative = binary[0] == 1;`
        # coordinate is 4 bytes. coordinate[0] is the most significant byte (if Big Endian).
        # If the MSB has the highest bit set, it's negative.
        # `to_sint4` (struct.unpack('>i')) already handles two's complement for signed integers.
        # But let's look at C# logic again.
        # `convertedCoordinate = coordinate.ToSInt4();` -> getting the int value.
        # THEN it checks `isNegative`.
        # IF `isNegative` -> `convertedCoordinate *= -1`.
        # This implies `convertedCoordinate` was interpreted as positive initially?
        # Or maybe the protocol uses a specific way to sign coordinates that isn't standard 2's complement?
        # But `ToSInt4` returns a signed int.

        # If I look closely at C# implementation of `ToSInt4`:
        # `return BitConverter.ToInt32(bytes.Reverse().ToArray(), 0);` (This assumes Little Endian architecture for BitConverter, so reversing means Big Endian input).

        # The C# `GetCoordinate` function logic is:
        # double convertedCoordinate = coordinate.ToSInt4();
        # string binary = Convert.ToString(coordinate[0], 2).PadLeft(8, '0');
        # bool isNegative = binary[0] == 1; # This is checking bit '1' (char) which is 49. Wait '1' is char.
        # `binary[0] == 1` -> checking if char is equal to integer 1? No, `binary[0]` is a char.
        # If the code was `binary[0] == '1'`, then it checks if MSB is 1.
        # If `binary[0] == 1`, it compares char (approx 48 or 49) with int 1. They are never equal.
        # So `isNegative` would always be False?
        # Unless `binary` is a byte array? No, `Convert.ToString` returns string.
        # This looks like a BUG in the C# code provided? Or maybe I am misinterpreting `binary[0] == 1`.
        # If `binary[0]` is '1', the char code is 49. 49 != 1.

        # However, assuming standard Teltonika protocol:
        # Teltonika coordinates are usually signed integers (2's complement) divided by 10000000.
        # If `to_sint4` correctly interprets 2's complement, we don't need the manual check unless the protocol uses sign-magnitude or something else.

        # Let's assume `to_sint4` works as expected for Big Endian signed 32-bit int.
        # If the C# code was trying to handle it manually, it might be redundant or wrong.
        # I will stick to `to_sint4` / 10000000.0.

        return float(converted_coordinate) / 10000000.0

    def map_data_packets(self, device_message: DeviceMessageEntity, reader: ByteReader,
                         teltonika_codec_configuration: TeltonikaCodecConfiguration,
                         data_packet_bytes: Optional[int] = None):

        number_of_data_packets = self.get_number_of_data_packets(reader, teltonika_codec_configuration, data_packet_bytes)

        for _ in range(number_of_data_packets):
            if teltonika_codec_configuration.data_packet_id_bytes == 1:
                id_ = reader.get_one()
            else:
                id_ = to_sshort2(reader.get(2))

            if data_packet_bytes is not None:
                length = data_packet_bytes
            else:
                length = to_sshort2(reader.get(2))

            value = reader.get(length)

            self.map_data_packet(id_, value, device_message)

    def map_data_packet(self, id_: int, value: bytes, device_message: DeviceMessageEntity):
        try:
            # Python switch-case equivalent
            if id_ == 1:
                device_message.additional_data_dic[str(TeltonikaDataIds.DigitalInput1)] = str(to_boolean(value))
            elif id_ == 11:
                device_message.additional_data_dic[str(TeltonikaDataIds.ICCID1)] = str(to_ulong8(value))
            elif id_ == 14:
                device_message.additional_data_dic[str(TeltonikaDataIds.ICCID2)] = str(to_ulong8(value))
            elif id_ == 15:
                device_message.additional_data_dic[str(TeltonikaDataIds.EcoScore)] = str(to_ushort2(value) * 0.01)
            elif id_ == TeltonikaDataIds.TotalOdometer:
                device_message.device_odometer = to_sint4(value)
            elif id_ == TeltonikaDataIds.GsmSignal:
                device_message.gsm_signal_level = to_ubyte1(value)
            elif id_ == 24:
                device_message.additional_data_dic[str(TeltonikaDataIds.GNSSSpeed)] = str(to_ushort2(value))
            elif id_ == TeltonikaDataIds.ExternalVoltage:
                device_message.vehicle_voltage = to_sshort2(value) * 0.001
            elif id_ == TeltonikaDataIds.BatteryVoltage:
                device_message.device_battery_voltage = to_ushort2(value) * 0.001
            elif id_ == TeltonikaDataIds.BatteryCurrent:
                device_message.device_battery_current = to_ushort2(value) * 0.001
            elif id_ == 69:
                val = to_ubyte1(value)
                device_message.additional_data_dic[str(TeltonikaDataIds.GNSSStatus)] = str(val)
                device_message.valid = (val == 1)
            elif id_ == TeltonikaDataIds.BatteryLevel:
                device_message.device_battery_level = to_ubyte1(value)
            elif id_ == TeltonikaDataIds.GNSSPDOP:
                device_message.pdop = to_ushort2(value) * 0.1
            elif id_ == TeltonikaDataIds.GNSSHDOP:
                device_message.hdop = to_ushort2(value) * 0.1
            elif id_ == 199:
                device_message.additional_data_dic[str(TeltonikaDataIds.TripOdometer)] = str(to_uint4(value))
            elif id_ == 200:
                device_message.additional_data_dic[str(TeltonikaDataIds.SleepMode)] = str(to_ubyte1(value))
            elif id_ == 205:
                device_message.additional_data_dic[str(TeltonikaDataIds.GsmCellId)] = str(to_ushort2(value))
            elif id_ == 206:
                device_message.additional_data_dic[str(TeltonikaDataIds.GsmAreaCode)] = str(to_ushort2(value))
            elif id_ == TeltonikaDataIds.Ignition:
                device_message.vehicle_ignition = to_boolean(value)
            elif id_ == 240:
                device_message.additional_data_dic[str(TeltonikaDataIds.Movement)] = str(to_boolean(value))
            elif id_ == TeltonikaDataIds.ActiveGSMOperator:
                home_network_identity = str(to_uint4(value))
                if len(home_network_identity) > 4:
                    device_message.gsm_mobile_country_code = home_network_identity[:3]
                    device_message.gsm_mobile_network_code = home_network_identity[3:]
            elif id_ == 636:
                 device_message.additional_data_dic[str(TeltonikaDataIds.UMTSLTECellID)] = str(to_uint4(value))

            # Event I/O
            elif id_ == 250:
                 device_message.additional_data_dic[str(TeltonikaDataIds.EventTrip)] = str(to_ubyte1(value))
            elif id_ == TeltonikaDataIds.IgnitionOnCounter:
                device_message.vehicle_ignition_duration = to_sint4(value)

            # OBD
            elif id_ == 30:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdDtcCount)] = str(to_ubyte1(value))
            elif id_ == 31:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdEngineLoad)] = str(to_ubyte1(value))
            elif id_ == 32:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdCoolantTemperature)] = str(to_sbyte1(value))
            elif id_ == 33:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdShortTermFuelTrim)] = str(to_sbyte1(value))
            elif id_ == 34:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdFuelPressure)] = str(to_ulong8(value))
            elif id_ == 35:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdIntakeManifoldAbsolutPressure)] = str(to_ubyte1(value))
            elif id_ == 36:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdEngineRpm)] = str(to_ushort2(value))
            elif id_ == 37:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdSpeed)] = str(to_ubyte1(value))
            elif id_ == 38:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdTimingAdvance)] = str(to_sbyte1(value))
            elif id_ == 39:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdIntakeAirTemperature)] = str(to_sbyte1(value))
            elif id_ == 40:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdMAFAirFlowRate)] = str(to_ushort2(value))
            elif id_ == 41:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdThrottlePosition)] = str(to_ubyte1(value))
            elif id_ == 42:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdRuntimeSinceEngineStart)] = str(to_ushort2(value))
            elif id_ == 43:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdDistanceTraveledMILOn)] = str(to_ushort2(value))
            elif id_ == 44:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdRelativeFuelRailPressure)] = str(to_ushort2(value) * 0.1)
            elif id_ == 45:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdDirectFuelRailPressure)] = str(to_ushort2(value) * 10)
            elif id_ == 46:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdCommandedEGR)] = str(to_ubyte1(value))
            elif id_ == 47:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdEGRError)] = str(to_sbyte1(value))
            elif id_ == 48:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdFuelLevel)] = str(to_ubyte1(value))
            elif id_ == 49:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdDistanceSinceCodesClear)] = str(to_ushort2(value))
            elif id_ == 50:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdBarometicPressure)] = str(to_ubyte1(value))
            elif id_ == 51:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdControlModuleVoltage)] = str(to_ushort2(value))
            elif id_ == 52:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdAbsoluteLoadValue)] = str(to_ushort2(value))
            elif id_ == 53:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdAmbientAirTemperature)] = str(to_sbyte1(value))
            elif id_ == 54:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdTimeRunWithMILOn)] = str(to_ushort2(value))
            elif id_ == 55:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdTimeSinceCodesCleared)] = str(to_ushort2(value))
            elif id_ == 56:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdAbsoluteFuelRailPressure)] = str(to_ushort2(value))
            elif id_ == 57:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdHybridBatteryPackLife)] = str(to_ubyte1(value))
            elif id_ == 58:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdEngineOilTemperature)] = str(to_ubyte1(value))
            elif id_ == 59:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdFuelInjectionTiming)] = str(to_sshort2(value) * 0.01)
            elif id_ == 60:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdFuelRate)] = str(to_ushort2(value))
            elif id_ == 256:
                device_message.additional_data_dic[str(TeltonikaDataIds.ObdVIN)] = StringUtil.convert_byte_array_to_string(value)
            elif id_ == 281:
                device_message.additional_data_dic[str(TeltonikaDataIds.ObdFaultCodes)] = StringUtil.convert_byte_array_to_string(value)
            elif id_ == 540:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdThrottlePositionGroup)] = str(to_ubyte1(value))
            elif id_ == 541:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdCommandedEquivalenceRatio)] = str(to_ubyte1(value))
            elif id_ == 542:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdIntakeMAP2Bytes)] = str(to_ushort2(value))
            elif id_ == 543:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdHybridSystemVoltage)] = str(to_ushort2(value))
            elif id_ == 544:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdHybridSystemCurrent)] = str(to_sshort2(value))
            elif id_ == 759:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdFuelType)] = str(to_ubyte1(value))

            # OBD OEM
            elif id_ == TeltonikaDataIds.ObdOemMileage:
                device_message.vehicle_odometer = to_sint4(value)
            elif id_ == 390:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemFuelLevel)] = str(to_uint4(value) * 0.1)
            elif id_ == 402:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemDistanceUntilService)] = str(to_uint4(value))
            elif id_ == 410:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemBatteryChargeState)] = str(to_ubyte1(value))
            elif id_ == 411:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemBatteryLevel)] = str(to_ubyte1(value))
            elif id_ == 412:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemBatteryPowerConsumption)] = str(to_ushort2(value))
            elif id_ == 755:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemRemainingDistance)] = str(to_ushort2(value))
            elif id_ == 1151:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemBatteryStateOfHealth)] = str(to_ushort2(value))
            elif id_ == 1152:
                 device_message.additional_data_dic[str(TeltonikaDataIds.ObdOemBatteryTemperature)] = str(to_sshort2(value))

            # CAN adapters
            elif id_ == 90:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanDoorStatus)] = str(to_sshort2(value))
            elif id_ == 100:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanProgramNumber)] = str(to_uint4(value))
            elif id_ == TeltonikaDataIds.CanFuelConsumedCounted:
                device_message.vehicle_fuel_consumption = to_sint4(value) * 0.1
            elif id_ == 123:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanControlStateFlags)] = str(to_uint4(value))
            elif id_ == 124:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanAgriculturalMachineryFlags)] = str(to_ulong8(value))
            elif id_ == 132:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanSecurityStateFlags)] = str(to_ulong8(value))
            elif id_ == 232:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanCNGStatus)] = str(to_ubyte1(value))
            elif id_ == 517:
                 device_message.additional_data_dic[str(TeltonikaDataIds.CanSecurityStateFlagsP4)] = str(to_ulong8(value))

            else:
                # Default case, handle unhandled data
                pass

        except Exception as e:
            # handle exception
            pass

    def get_number_of_data_packets(self, reader: ByteReader,
                                   teltonika_codec_configuration: TeltonikaCodecConfiguration,
                                   data_packet_bytes: Optional[int]) -> int:
        if data_packet_bytes is not None:
            if teltonika_codec_configuration.data_packet_bytes == 1:
                return reader.get_one()
            else:
                return to_sshort2(reader.get(2))

        if teltonika_codec_configuration.has_variable_data_packets:
            return to_sshort2(reader.get(2))

        return 0
