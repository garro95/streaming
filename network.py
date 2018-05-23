import simpy;
import random;

class Network(object):
    """Documentation for Network

    """
    def __init__(self, RTT, env):
        super(Network, self).__init__()
        self.RTT = RTT
        self.env = env

    def send(self, receiver, data):
        yield self.env.timeout(self.RTT/2)
        receiver.incoming_data=data
        self.env.process(receiver.incoming_packet)
