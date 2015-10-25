from operator import attrgetter


class Channel():
    """ A Mumble channel object """

    # Map of class instance vars to protobuf props
    _properties = {
        'channel_id': 'channel_id',
        'name':       'name',
        'parent_id':  'parent',
        'position':   'position'
    }

    def __init__(self, client):
        """
        :param client: Hiss Client instance
        :return:
        """
        self._client = client

        # Instance properties
        self.channel_id = None
        self.name = None
        self.parent_id = None
        self.position = None

    def update(self, message):
        """ Update the channel's state with the given message """

        for local_prop, proto_prof in self._properties.items():
            if not message.HasField(proto_prof):
                continue

            self.__dict__[local_prop] = getattr(message, proto_prof)

            # self._description
            # self._temporary
            # self._position
            # self._description_hash

            # self._links = []
            # self._links_add
            # self._links_remove

    def parent(self):
        """ Parent channel """
        return self._client.channels.get(self.parent_id)

    def _children(self):
        """ Any child channels. FIXME: Probably muchos more efficient way to do this """
        for channel in self._client.channels.values():
            if channel.parent_id is not None and channel.parent_id == self.channel_id:
                yield channel

    def children(self):
        """ Any child channels, sorted by their position """
        alphabetical_children = sorted(self._children(), key=attrgetter('name'))  # Secondary sort, alphabetical
        return sorted(alphabetical_children, key=lambda x: x.position)  # Primary sort, by position

        # def users(self):
        #     """ Users in this channel """
        #     return [user for user in self._client.users where users.channel_id = self.channel_id]
        #     pass
