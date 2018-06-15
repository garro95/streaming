#!/usr/bin/python3
import simpy
from client import Client
from network import Network
from server import Server
import random
import matplotlib.pyplot as plt

# The client will download K packets before starting
# the player
# REMEMBER: waiting time is related to network speed, not
# to video to play
S = 6  # Duration of the video contained in a packet
K = 20  # Number of packets in the client buffer
RTT = 0.5
OB = 1000  # Mb Output buffer capacity of the server
MAX_QUALITY = 4
INTER_ARRIVAL_TIME = 10  # Seconds
DURATION = 1000  # Seconds
WAIT_TIME = 15  # Seconds
SERV_SPEED = 15000  # Mbps
CLI_SPEED = 70  # Mbps
RUN_TIME = 5000


class ClientSpawner(object):
    """Documentation for ClientSpawner

    """
    def __init__(self, inter_arrival_time, duration,
                 wait_time, network, server):
        super(ClientSpawner, self).__init__()
        self.inter_arrival_time = inter_arrival_time
        self.duration = duration
        self.wait_time = wait_time
        self.network = network
        self.server = server

    def run(self, env):
        self.count = 0
        while True:
            duration = random.normalvariate(self.duration, 200)
            duration -= duration%S
            wait_time = random.expovariate(1.0/self.wait_time)
            client = Client(S, K, self.server, self.network, env,
                            MAX_QUALITY, CLI_SPEED, duration, wait_time, self.count)
            env.process(client.run())
            self.count += 1
            yield env.timeout(random.expovariate(1.0/self.inter_arrival_time))


def main():
    random.seed(12)
    env = simpy.Environment()
    network = Network(RTT, env)
    server = Server(network, S, SERV_SPEED, OB, env)
    clientspawn = ClientSpawner(INTER_ARRIVAL_TIME, DURATION, WAIT_TIME,
                                network, server)
    env.process(clientspawn.run(env))
    env.run(RUN_TIME)
    plt.figure()
    plt.plot(server.time, server.buf_sz)
    plt.figure()
    plt.plot(server.time_clients, server.nclients)
    plt.show()


if __name__ == '__main__':
    main()
