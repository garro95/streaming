class Client(object):
    """Simulate the client, that is the arrival process

    """
    def __init__(self, S, K, Server, Network, environment, max_quality, duration, wait_time):
        super(Client, self).__init__()
        self.S = S
        self.buf_cap = K #...acity
        self.server = Server
        self.network = Network
        self.buf_size = 0
        self.quality = 0
        self.env = environment
        self.max_quality = max_quality
        self.duration = duration
        self.wait_time = wait_time
        self.timeout_error = False
    def run(self):
        #start-up
        for i in range(self.buf_cap):
            req = self.request(quality)
            self.network.send(self.server, req)
            t0 = self.env.now()
            yield
        #steady state
        self.env.process(self.play())
        while self.duration > 0:
            t1 = self.env.now()
            if t1-t0 < self.S:
                if self.quality < self.max_quality:
                    self.quality += 1
            else:
                if self.quality > 0:
                    self.quality -= 1
            if self.duration > self.buf_size * self.S:
                req = self.request(self.quality)
                self.network.send(self.server, req)

    def request(self, quality):
        req = quality

    def incoming_packet(self, data):
        if data == "ERROR":
            pass
        else:
            self.buf_size += 1
            self.timeout_error = False
            self.run()

    def play(self):
        while self.duration > 0:
            if self.buf_size > 0:
                yield self.env.timeout(self.S)
                self.buf_size -= 1
                self.duration -= self.S
            else:
                self.timeout_error = True
                yield self.env.timeout(self.wait_time)
                if self.timeout_error:
                    break
        
        print("video finito")
