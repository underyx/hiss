import ssl
import time
import struct
import asyncio
import platform
import functools
import collections

from . import Mumble_pb2
from .constants import MESSAGE_TYPES
from .channel import Channel


class Client:
    version = (1, 3, 0)

    def __init__(self, host, port=64738, username='snek', password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._reader = None
        self._writer = None
        self._callbacks = collections.defaultdict(list)

        # Server state
        self.channels = {}
        # self.users = {}
        self.bind_state_tracking()

    def run(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.connect())
        asyncio.ensure_future(self.read_messages())
        loop.run_forever()

    def bind(self, message_type):
        """ Decorator to bind methods to Mumble events (see `constants.MESSAGE_TYPES`) """

        def wrapper(function):
            self._callbacks[message_type].append(function)
            return function

        return wrapper

    def bind_command(self, command):
        """ Decorator to bind methods to text messages starting with the given `command`. """

        def wrapper(function):
            @functools.wraps(function)
            def decorator(message):
                if message.message.lower().startswith(command):
                    function(message)

            self._callbacks['TextMessage'].append(decorator)

            return decorator

        return wrapper

    async def _send(self, message):
        """ Send a message to the server. `message` is a pprotobuf object from the `Mumble_pb2` module. """
        message_type = MESSAGE_TYPES[message.__class__.__name__]
        body = message.SerializeToString()
        header = struct.pack('>HI', message_type, len(body))
        self._writer.write(header + body)
        await self._writer.drain()

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port, ssl=ssl_context)

        await self.exchange_version()
        await self.authenticate()
        await self.keep_alive()

    async def exchange_version(self):
        message = Mumble_pb2.Version()
        message.release = '.'.join(str(part) for part in self.version)
        message.version = (self.version[0] << 16) + (self.version[1] << 8) + self.version[0]
        message.os = platform.system()
        message.os_version = platform.release()
        await self._send(message)

    async def authenticate(self):
        message = Mumble_pb2.Authenticate()
        message.username = self.username
        if self.password:
            message.password = self.password
        await self._send(message)

    async def keep_alive(self):
        message = Mumble_pb2.Ping()
        message.timestamp = int(time.time())
        while True:
            await self._send(message)
            await asyncio.sleep(1)

    async def read_messages(self):
        while True:
            if self._reader is None:
                await asyncio.sleep(0.1)
                continue

            try:
                header = await self._reader.readexactly(6)
            except asyncio.IncompleteReadError:
                await asyncio.sleep(0.1)
                continue

            message_type_code, body_length = struct.unpack('>HI', header)
            message_type = MESSAGE_TYPES[message_type_code]
            body = await self._reader.readexactly(body_length)
            message = getattr(Mumble_pb2, message_type)()
            message.ParseFromString(body)

            for callback in self._callbacks[message_type]:
                callback(message)

    def update_channel_state(self, message):
        """ Keep track of channel states """

        channel_id = message.channel_id
        channel = self.channels.get(channel_id)
        if channel is None:
            channel = Channel(self)
            self.channels[channel_id] = channel

        channel.update(message)

    def bind_state_tracking(self):
        """ Bind any internal state tracking methods to their associated events """

        self._callbacks['ChannelState'].append(self.update_channel_state)
