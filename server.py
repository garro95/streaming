from network import Data
from simpy import Resource


class Server(object):
    """Documentation for Server

    """
    def __init__(self, network, S, speed, outbuf_cap, environment):
        super(Server, self).__init__()
        self.quality_levels = [1.5*S, 4.0*S, 7.5*S, 12*S, 68*S]
        self.network = network
        self.S = S
        self.outbuf_cap = outbuf_cap
        self.outbuf_size = 0
        self.env = environment
        self.speed = speed  # Mbps
        self.network_interface = Resource(self.env, 1)
        self.buf_sz = []
        self.time = []
        self.nclientsN = 0
        self.nclients = []
        self.time_clients = []
        self.sender = None
        self.data = None

    def incoming_packet(self, sender, data):
        #print("packet received from client: ", self.incoming_data)
        self.sender = sender
        self.data = data
        quality = self.data.content
        timestamp = self.data.timestamp
        if self.outbuf_size + self.quality_levels[quality] > self.outbuf_cap:
            yield self.env.process(self.network.send(self, self.sender,
                                                     Data(0, "ERROR", timestamp)))
        else:
            yield self.env.process(self.process(self.sender, quality, timestamp))

    def process(self, sender, quality, timestamp):
        self.outbuf_size += self.quality_levels[quality]
        self.buf_sz.append(self.outbuf_size)
        self.time.append(self.env.now)
        with self.network_interface.request() as req:
            yield req
            yield self.env.process(self.network.send(self, sender,
                                    Data(self.quality_levels[quality], "", timestamp, quality)))
        self.outbuf_size -= self.quality_levels[quality]
