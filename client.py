class Client(object):
    """Simulate the client, that is the arrival process

    """
    K = 10
    def __init__(self, S):
        super(Client, self).__init__()
        self.S = S
    def run(self, env, network):
        quality = 0
        buffer_size= 0
        for i in range(K):
            t0 = env.now()
            self.request(quality, t0)
            
    def request(self, quality):
        
