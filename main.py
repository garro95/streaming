#!/usr/bin/python3
import simpy
from client import Client
from network import Network
from server import Server
import random

# The client will download K packets before starting
# the player
# REMEMBER: waiting time is related to network speed, not
# to video to play
S = 6  # Duration of the video contained in a packet
K = 20  # Number of packets in the client buffer
RTT = 0.05
OB = 75000  # Mb Output buffer capacity of the server
MAX_QUALITY = 4
INTER_ARRIVAL_TIME = 8  # Seconds
DURATION = 5228  # Seconds
WAIT_TIME = 90  # Seconds
SERV_SPEED = 25000  # Mbps
CLI_SPEED = 9  # Mbps


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
            duration = random.expovariate(1.0/self.duration)
            wait_time = random.expovariate(1.0/self.wait_time)
            client = Client(S, K, self.server, self.network, env,
                            MAX_QUALITY, CLI_SPEED, duration, wait_time)
            env.process(client.run())
            self.count += 1
            yield env.timeout(random.expovariate(1.0/self.inter_arrival_time))


def main():
    random.seed(12)
    env = simpy.Environment()
    network = Network(RTT, env)
    server = Server(network, S, SERV_SPEED, OB, env)
    clientspown = ClientSpawner(INTER_ARRIVAL_TIME, DURATION, WAIT_TIME,
                                network, server)
    env.process(clientspown.run(env))
    env.run(100000)
    print(clientspown.count)


if __name__ == '__main__':
    main()
