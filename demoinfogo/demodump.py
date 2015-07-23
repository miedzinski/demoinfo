import struct

from .netmessages_public_pb2 import *
from .cstrike15_usermessages_public_pb2 import *

from .demofile import DemoError, DemoMsg, DemoFile


class DemoDump(object):

    def __init__(self, demo):
        self.demo = DemoFile(demo)

        self.NET_MSG = {
            net_NOP: [],
            net_Disconnect: [],  # disconnect, last message in connection
            net_File: [],  # file transmission message request/deny
            net_Tick: [],  # s->c world tick, c->s ack world tick
            net_StringCmd: [],  # a string command
            net_SetConVar: [],  # sends one/multiple convar/userinfo settings
            net_SignonState: [],  # signals or acks current signon state
        }
        self.SVC_MSG = {
            svc_ServerInfo: [],  # first message from server about game; map etc
            svc_SendTable: [],  # sends a sendtable description for a game class
            svc_ClassInfo: [],  # Info about classes (first byte is a CLASSINFO_ define).
            svc_SetPause: [],  # tells client if server paused or unpaused
            svc_CreateStringTable: [],  # inits shared string tables
            svc_UpdateStringTable: [],  # updates a string table
            svc_VoiceInit: [],  # inits used voice codecs & quality
            svc_VoiceData: [],  # Voicestream data from the server
            svc_Print: [],  # print text to console
            svc_Sounds: [],  # starts playing sound
            svc_SetView: [],  # sets entity as point of view
            svc_FixAngle: [],  # sets/corrects players viewangle
            svc_CrosshairAngle: [],  # adjusts crosshair in auto aim mode to lock on traget
            svc_BSPDecal: [],  # add a static decal to the world BSP
            svc_UserMessage: [],  # a game specific message
            svc_GameEvent: [],  # global game event fired
            svc_PacketEntities: [],  # non-delta compressed entities
            svc_TempEntities: [],  # non-reliable event object
            svc_Prefetch: [],  # only sound indices for now
            svc_Menu: [],  # display a menu from a plugin
            svc_GameEventList: [],  # list of known games events and fields
            svc_GetCvarValue: [],  # Server wants to know the value of a cvar on the client
        }

    def register_on_netmsg(self, msg, callback):
        if msg not in self.NET_MSG:
            raise DemoError('Net message not found')
        self.NET_MSG[msg].append(callback)

    def register_on_svcmsg(self, msg, callback):
        if msg not in self.SVC_MSG:
            raise DemoError('Server message not found')
        self.SVC_MSG[msg].append(callback)

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
            if cmd in self.NET_MSG:
                for callback in self.NET_MSG[cmd]:
                    callback(cmd, data)
            if cmd in self.SVC_MSG:
                for callback in self.SVC_MSG[cmd]:
                    callback(cmd, data)
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
