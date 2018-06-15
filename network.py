class Network(object):
    """Documentation for Network

    """
    def __init__(self, RTT, env):
        super(Network, self).__init__()
        self.RTT = RTT
        self.env = env

    def send(self, sender, receiver, data):
        yield self.env.timeout(data.size/sender.speed)
        self.env.process(self.send1(sender, receiver, data))

    def send1(self, sender, receiver, data):
        yield self.env.timeout(self.RTT/2)
        yield self.env.timeout(data.size/receiver.speed)
        self.env.process(receiver.incoming_packet(sender, data))


class Data(object):
    """Documentation for Data

    """
    def __init__(self, size, content, timestamp, level = 0):
        super(Data, self).__init__()
        self.size = size
        self.content = content
        self.timestamp = timestamp
        self.level = level

    def __str__(self):
        return "size: " + str(self.size) + " content: " + str(self.content)
