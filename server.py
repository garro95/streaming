from network import Data
from simpy import Resource


class Server(object):
    """Documentation for Server

    """
    def __init__(self, network, S, speed, outbuf_cap, environment):
        super(Server, self).__init__()
        self.quality_levels = [1.750*S, 3.0*S, 5.0*S, 6.35*S, 12.0*S]
        self.network = network
        self.S = S
        self.outbuf_cap = outbuf_cap
        self.outbuf_size = 0
        self.env = environment
        self.speed = speed  # Mbps
        self.network_interface = Resource(self.env, 1)

    def incoming_packet(self):
        # TODO: consider that the queue should not overflow
        print("packet received from client: ", self.incoming_data)
        quality = self.incoming_data.content
        if self.outbuf_size + self.quality_levels[quality] > self.outbuf_cap:
            yield self.env.process(self.network.send(self, self.sender,
                                                     Data(0, "ERROR")))
        else:
            yield self.env.process(self.process(self.sender, quality))

    def process(self, sender, quality):
        self.outbuf_size += self.quality_levels[quality]
        with self.network_interface.request() as req:
            yield req
            yield self.env.process(self.network.send(self, sender,
                                                     Data(self.quality_levels[quality], "")))
        self.outbuf_size -= self.quality_levels[quality]
