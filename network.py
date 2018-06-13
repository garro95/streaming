class Network(object):
    """Documentation for Network

    """
    def __init__(self, RTT, env):
        super(Network, self).__init__()
        self.RTT = RTT
        self.env = env

    def send(self, sender, receiver, data):
        # print("sending packet from ", sender, " to ", receiver)
        yield self.env.timeout(self.RTT/2)
        yield self.env.timeout(data.size/sender.speed)
        yield self.env.timeout(data.size/receiver.speed)
        receiver.incoming_data = data
        receiver.sender = sender
        self.env.process(receiver.incoming_packet())


class Data(object):
    """Documentation for Data

    """
    def __init__(self, size, content):
        super(Data, self).__init__()
        self.size = size
        self.content = content

    def __str__(self):
        return "size: " + str(self.size) + " content: " + str(self.content)
