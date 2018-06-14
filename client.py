from network import Data


class Client(object):
    """Simulate the client, that is the arrival process

    """
    def __init__(self, S, K, Server, Network, environment,
                 max_quality, speed, duration, wait_time):
        super(Client, self).__init__()
        self.speed = speed  # Mbps
        self.S = S
        self.buf_cap = K  # ...acity
        self.server = Server
        self.network = Network
        self.buf_size = 0
        self.quality = 0
        self.env = environment
        self.max_quality = max_quality
        self.duration = duration
        self.wait_time = wait_time
        self.timeout_error = False
        self.consumed_event = self.env.event()
        self.refilled_event = self.env.event()
        self.received_event = self.env.event()

    def run(self):
        # start-up
        print("Buffering...")
        for i in range(self.buf_cap):
            # print("cose ", self.env.now)
            req = self.request(0)
            self.t0 = self.env.now
            yield self.env.process(self.network.send(self, self.server,
                                                     Data(0, req)))
            self.received_event = self.env.event()
            yield self.received_event
        # steady state
        self.env.process(self.play())
        # TODO: check that the buffer has room
        self.quality = 0
        while self.duration > self.buf_size * self.S:
            if self.buf_size == self.buf_cap:
                yield self.consumed_event
            self.t0 = self.env.now
            req = self.request(self.quality)
            yield self.env.process(self.network.send(self, self.server,
                                                     Data(0, req)))
            self.received_event = self.env.event()
            yield self.received_event

    def request(self, quality):
        return quality

    def incoming_packet(self):
        # print("Packet received from server: ", self.env.now)
        if self.incoming_data.content == "ERROR":
            if self.quality > 0:
                self.quality -= 1
                self.received_event.succeed()
        else:
            self.buf_size += 1
            t1 = self.env.now
            if t1-self.t0 < self.S:
                if self.quality < self.max_quality:
                    self.quality += 1
            else:
                if self.quality > 0:
                    self.quality -= 1
            if self.timeout_error:
                self.timeout_error = False
                self.refilled_event.succeed()
        self.received_event.succeed()
        yield self.env.timeout(0)

    def play(self):
        print("Playing back")
        while self.duration > 0:
            if self.buf_size > 0:
                yield self.env.timeout(self.S)
                self.buf_size -= 1
                self.duration -= self.S
                if self.buf_size == self.buf_cap-1:
                    self.consumed_event.succeed()
            else:
                self.timeout_error = True
                self.refilled_event = self.env.event()
                yield self.env.any_of([self.env.timeout(self.wait_time),
                                       self.refilled_event])
                if self.timeout_error:
                    break
        if self.timeout_error:
            print("Churning")
            self.duration = 0
            return
        print("video is over")
