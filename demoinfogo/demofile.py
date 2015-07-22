import struct


MAXOSPATH = 260
DEMOHEADER = 'HL2DEMO'
DEMOPROTOCOL = 4

MAXSPLITSCREENCLIENTS = 2


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

    def __init__(self, demofile):
        self.file = demofile

        fmt = '@8sii{0}s{0}s{0}s{0}sfiii'.format(MAXOSPATH)
        data = struct.unpack(fmt, self.file.read(struct.calcsize(fmt)))
        self.header = DemoHeader(*list(data))

        if self.header.demofilestamp != DEMOHEADER:
            raise DemoError('Invalid demo header')

        if self.header.demoprotocol != DEMOPROTOCOL:
            raise DemoError('Unsupported protocol')

    def _read_struct(self, fmt):
        return struct.unpack(fmt, self.file.read(struct.calcsize(fmt)))[0]

    def read_raw_data(self):
        size = self._read_struct('@i')
        data = self.file.read(size)

        return size, data

    def read_sequence_info(self):
        seq_nr_in = self._read_struct('@i')
        seq_nr_out = self._read_struct('@i')

        return seq_nr_in, seq_nr_out

    def read_cmd_info(self):
        fmt = '@{}'.format('iffffffffffffffffff' * MAXSPLITSCREENCLIENTS)

        return self._read_struct(fmt)

    def read_cmd_header(self):
        cmd = self._read_struct('@B')
        if cmd <= 0:
            cmd = DemoMsg.dem_stop
            return cmd, 0, 0
        tick = self._read_struct('@i')
        player_slot = self._read_struct('@B')

        return cmd, tick, player_slot

    def read_user_cmd(self):
        outgoing_sequence = self._read_struct('@i')
        size, data = self.read_raw_data()

        return outgoing_sequence, size, data
