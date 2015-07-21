import struct

from . import netmessages_public_pb2
from . import cstrike15_usermessages_public_pb2


MAXOSPATH = 260
DEMOHEADER = 'HL2DEMO'
DEMOPROTOCOL = 4


class DemoError(Exception):
    pass


class DemoMsg:

    # it's a startup message, process as fast as possible
    dem_signon = 1
    # it's a normal network packet that we stored off
    dem_packet = 2
    # sync client clock to demo tick
    dem_synctick = 3
    # console command
    dem_consolecmd = 4
    # user input command
    dem_usercmd = 5
    # network data tables
    dem_datatables = 6
    # end of time.
    dem_stop = 7
    # a blob of binary data understood by a callback function
    dem_customdata = 8
    dem_stringtables = 9
    # Last command
    dem_lastcmd = dem_stringtables


class DemoHeader(object):

    def __init__(self, demofilestamp, demoprotocol, networkprotocol,
                 servername, clientname, mapname, gamedirectory,
                 playback_time, playback_ticks, playback_frames, signonlength):
        # Should be HL2DEMO
        self.demofilestamp = demofilestamp.decode().rstrip('\0')
        # Should be DEMOPROTOCOL
        self.demoprotocol = demoprotocol
        # Should be PROTOCOL_VERSION
        self.networkprotocol = networkprotocol
        # Name of server
        self.servername = servername.decode().rstrip('\0')
        # Name of client who recorded the game
        self.clientname = clientname.decode().rstrip('\0')
        # Name of map
        self.mapname = mapname.decode().rstrip('\0')
        # Name of game directory (com_gamedir)
        self.gamedirectory = gamedirectory.decode().rstrip('\0')
        # Time of track
        self.playback_time = playback_time
        # # of ticks in track
        self.playback_ticks = playback_ticks
        # # of frames in track
        self.playback_frames = playback_frames
        # length of sigon data
        self.signonlength = signonlength


class DemoFile(object):

    def __init__(self, path):
        self.file = open(path, 'rb')

        demoheader = struct.Struct('@8sii{0}s{0}s{0}s{0}sfiii'.format(MAXOSPATH))
        data = demoheader.unpack_from(self.file.read(demoheader.size))
        self.header = DemoHeader(*list(data))

        if self.header.demofilestamp != DEMOHEADER:
            raise DemoError('Invalid demo header')

        if self.header.demoprotocol != DEMOPROTOCOL:
            raise DemoError('Unsupported protocol')

        self.offset = demoheader.size

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()
