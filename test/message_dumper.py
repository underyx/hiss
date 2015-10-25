from hiss.client import Client
from hiss.constants import MESSAGE_TYPES
from os import getenv

host = getenv('MUMBLE_SERVER')
user = getenv('MUMBLE_USER', 'snek')

client = Client(host, username=user)

# Get debuggy, dump all messages! Might be a cleaner way to do this.
def log_message(type):
    """ Return a logger function for the given message type """

    def _logger(message):
        print("Received {} message: {}".format(type, message))

    return _logger


# Bind logger function to all message types
for type in MESSAGE_TYPES.keys():
    # Skip ids, because underyx did weird things
    if isinstance(type, int):
        continue

    client._callbacks[type].append(log_message(type))

# Connect to the server and do ur thing
client.run()
