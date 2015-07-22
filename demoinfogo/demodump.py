import struct

from .netmessages_public_pb2 import *
from .cstrike15_usermessages_public_pb2 import *

from .demofile import DemoError, DemoMsg, DemoFile


class DemoDump(object):

    def __init__(self, demo):
        self.demo = DemoFile(demo)

    def do_dump(self):
        demo_finished = False

        while not demo_finished:
            cmd, tick, player_slot = self.demo.read_cmd_header()
            print('{} - {} - {}'.format(cmd, tick, player_slot))
            if cmd == DemoMsg.dem_signon:
                self._handle_demo_packet()
            elif cmd == DemoMsg.dem_packet:
                self._handle_demo_packet()
            elif cmd == DemoMsg.dem_synctick:
                continue
            elif cmd == DemoMsg.dem_consolecmd:
                self.demo.read_raw_data()
            elif cmd == DemoMsg.dem_usercmd:
                self.demo.read_user_cmd()
            elif cmd == DemoMsg.dem_datatables:
                self.demo.read_raw_data()
            elif cmd == DemoMsg.dem_stop:
                demo_finished = True
            elif cmd == DemoMsg.dem_stringtables:
                self.demo.read_raw_data()

    def _handle_demo_packet(self):
        self.demo.read_cmd_info()
        self.demo.read_sequence_info()
        # ignore results
        length, buf = self.demo.read_raw_data()

        if length > 0:
            self._dump_packet(buf, length)

    def _dump_packet(self, buf, length):
        index = 0

        while index < length:
            cmd, index = self._read_int32(buf, index)
            size, index = self._read_int32(buf, index)
            data = buf[index: index + size]
            # call events
            print(cmd)
            index += size

    def _read_int32(self, buf, index):
        count = 0
        result = 0

        while True:
            byte = struct.unpack_from('@B', buf, index)[0]
            index += 1
            result |= (byte & 0x7F) << (7 * count)
            count += 1
            if not byte & 0x80 or count == 5:
                break

        return result, index
