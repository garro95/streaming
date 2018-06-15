from network import Data
import matplotlib.pyplot as plt


class Client(object):
    """Simulate the client, that is the arrival process

    """
    def __init__(self, S, K, Server, Network, environment,
                 max_quality, speed, duration, wait_time, id):
        super(Client, self).__init__()
        self.quality_levels = [1.5, 4.0, 7.5, 12, 68]
        self.id = id
        self.speed = speed  # Mbps
        self.S = S
        self.buf_cap = K  # ...acity
        self.server = Server
        self.network = Network
        self.buf_size = 0
        self.quality = 0
        self.env = environment
        self.max_quality = max_quality
        self.length = duration
        self.duration = duration
        self.wait_time = wait_time
        self.timeout_error = False
        self.consumed_event = self.env.event()
        self.refilled_event = self.env.event()
        self.received_event = self.env.event()
        self.time_response = 0
        self.dl_speed = 0
        self.time_a = []
        self.buffer_a = []
        self.quality_a = []

    def run(self):
        # start-up
        # print("Buffering...")
        self.server.nclientsN += 1
        self.server.nclients.append(self.server.nclientsN)
        self.server.time_clients.append(self.env.now)
        while self.buf_size < self.buf_cap:
            self.buffer_a.append(self.buf_size)
            self.time_a.append(self.env.now)
            self.quality_a.append(0)
            req = self.request(0)
            yield self.env.process(self.network.send(self, self.server, req))
            self.received_event = self.env.event()
            yield self.received_event
        # steady state
        self.env.process(self.play())
        self.quality = 0
        while self.duration > self.buf_size * self.S:
            self.consumed_event = self.env.event()
            if self.buf_size == self.buf_cap:
                yield self.consumed_event
                self.consumed_event = self.env.event()
            req = self.request(self.quality)
            yield self.env.process(self.network.send(self, self.server,
                                                     req))
            self.received_event = self.env.event()
            yield self.received_event

    def request(self, quality):
        return Data(0, quality, self.env.now)

    def incoming_packet(self, sender, data):
        self.sender = sender
        self.data = data
        # print(self, ";", self.incoming_data.size)
        self.time_response = self.env.now
        if self.data.content == "ERROR":
            if self.quality > 0:
                self.quality -= 1
        else:
            self.buf_size += 1
            if self.calcSpeed(self.data.size, self.time_response - self.data.timestamp, self.data.level):
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

    def calcSpeed(self, dataSize, time, level):
        if time > self.S:
            # print("True, dl_speed = ", dlspeed, " quality = ", self.quality_levels[level])
            return True
        else:
            # print("False, dl_speed = ", dlspeed, " quality = ", self.quality_levels[level])
            return False

    def play(self):
        # print("Playing back")
        while self.duration > 0:
            if self.buf_size > 0:
                self.buffer_a.append(self.buf_size)
                self.time_a.append(self.env.now)
                self.quality_a.append(self.quality)
                yield self.env.timeout(self.S)
                self.buf_size -= 1
                self.duration -= self.S
                if self.buf_size == self.buf_cap - 1:
                    self.consumed_event.succeed()
            else:
                self.buffer_a.append(self.buf_size)
                self.time_a.append(self.env.now)
                self.quality_a.append(self.quality)
                self.timeout_error = True
                self.refilled_event = self.env.event()
                yield self.env.any_of([self.env.timeout(self.wait_time),
                                       self.refilled_event])
                if self.timeout_error:
                    break
        if self.timeout_error:
            self.buffer_a.append(self.buf_size)
            self.time_a.append(self.env.now)
            self.quality_a.append(0)
            print("Churning video long ", self.length , " with ", self.duration, " left, at ", self.env.now)
            self.duration = 0
            self.server.nclientsN -= 1
            self.server.nclients.append(self.server.nclientsN)
            self.server.time_clients.append(self.env.now)
            # plt.figure()
            # plt.plot(self.time_a, self.quality_a)
            # plt.plot(self.time_a, self.buffer_a)
            # plt.show()
            return
        self.buffer_a.append(self.buf_size)
        self.time_a.append(self.env.now)
        self.quality_a.append(0)
        print("Video long ", self.length, " is over at ", self.env.now)
        self.server.nclientsN -= 1
        self.server.nclients.append(self.server.nclientsN)
        self.server.time_clients.append(self.env.now)
        # plt.figure()
        # plt.plot(self.time_a, self.quality_a)
        # plt.plot(self.time_a, self.buffer_a)
        # plt.show()
#
