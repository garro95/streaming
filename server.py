from enum import Enum


class Server(object):
    """Documentation for Server

    """
    def __init__(self, network, S, outbuf_cap):
        super(Server, self).__init__()
        quality_levels = [1750*S, ]
        self.network = network
        self.S = S
        self.outbuf_cap = outbuf_cap
        self.outbuf_size = 0
        
    def incoming_packet(self):
        # TODO: consider that the queue should not overflow
        quality = self.incoming_data
        if outbuf_size >= outbuf_cap:
    
