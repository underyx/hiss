# hiss

A Mumble client library for Python 3.5

## Installation

    pip3.5 install hiss

## Usage

Initialize your client:

    import hiss
    client = hiss.Client('mumble-server.com')

Define what you want it to do and when:

    @client.bind('UserRemove')
    def log_kicks(message):
        print('{message.actor} kicked someone!'.format(message=message)

You can also bind to chat commands:

    @client.bind_command('!kick')
    def log_kick_commands(message):
        print('Someone wants to kick {user}!'.format(user=message.msg[6:]))

And once you have all your functions registered:

    client.run()
