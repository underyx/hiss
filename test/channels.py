import asyncio

from hiss.client import Client
from hiss.constants import MESSAGE_TYPES
from os import getenv
from hiss.Mumble_pb2 import TextMessage

host = getenv('MUMBLE_SERVER')
user = getenv('MUMBLE_USER', 'snek')

client = Client(host, username=user)


@client.bind_command('channels')
def command_channels(message):
    """ Visualise the channel structure """

    root_channel = client.channels.get(0)
    if not root_channel:
        return

    reply = TextMessage()
    reply.channel_id.append(root_channel.channel_id)  # TODO: Send to current channel
    reply.message = "<ul>{}</ul>".format(visualise_channel_relationships(root_channel))

    # print(message.message)
    asyncio.ensure_future(client._send(reply))


@client.bind_command('parent')
def command_parent(message):
    """ Find a channel by name and return its parent's name. Usage: `parent searchterm` """
    reply = TextMessage()
    reply.channel_id.append(0)  # TODO: Send to current channel

    search_name = message.message[len('parent') + 1:].strip()

    if len(search_name) == 0:
        reply.message = 'Please specify a search argument'
        return asyncio.ensure_future(client._send(reply))


    # Go through channels and find the first channel name containing the search term
    # Ye, not a very good search algorithm.
    matched_channel = None
    for channel in client.channels.values():
        if search_name.lower() not in channel.name.lower():
            continue

        # A match!
        matched_channel = channel
        break

    if matched_channel is None:
        reply.message = "Sorry, couldn't find a channel with that search term"
        return asyncio.ensure_future(client._send(reply))

    parent = matched_channel.parent()
    if parent is None:
        reply.message = "Channel <em>{}</em> does not have a parent!".format(matched_channel.name)
        return asyncio.ensure_future(client._send(reply))

    reply.message = "Channel <em>{}</em>'s parent is <em>{}</em>".format(matched_channel.name, parent.name)
    return asyncio.ensure_future(client._send(reply))


def visualise_channel_relationships(channel, nest_level=0):
    result = '<li>'
    result += channel.name

    for child in channel.children():
        result += '<ul>'
        result += visualise_channel_relationships(child, nest_level + 1)
        result += '</ul>'

    result += '</li>'

    return result


# Connect to the server and do ur thing
client.run()
