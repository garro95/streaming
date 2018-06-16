#!/usr/bin/python3
import simpy
from client import Client
from network import Network
from server import Server
import random
import matplotlib.pyplot as plt
from argparse import ArgumentParser

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
SEED = 12


class ClientSpawner(object):
    """Documentation for ClientSpawner

    """
    def __init__(self, inter_arrival_time, duration,
                 wait_time, network, server, cli_speed):
        super(ClientSpawner, self).__init__()
        self.inter_arrival_time = inter_arrival_time
        self.duration = duration
        self.wait_time = wait_time
        self.network = network
        self.server = server
        self.cli_speed = cli_speed

    def run(self, env):
        self.count = 0
        while True:
            duration = random.normalvariate(self.duration, 200)
            duration -= duration % S
            wait_time = random.expovariate(1.0/self.wait_time)
            client = Client(S, K, self.server, self.network, env,
                            MAX_QUALITY, self.cli_speed, duration,
                            wait_time, self.count)
            env.process(client.run())
            self.count += 1
            yield env.timeout(random.expovariate(1.0/self.inter_arrival_time))


def main():
    parser = ArgumentParser()
    parser.add_argument("S", "-S",
                        help="The duration of a fragment of video, in seconds",
                        default=S, type=float)
    parser.add_argument("K", "-k",
                        help="The length of the client buffer, in number of fragments",
                        default=K, type=int)
    parser.add_argument("RTT", "--rtt", "-R",
                        help="The round trip time between server and client, in seconds",
                        default=RTT, type=float)
    parser.add_argument("SEED", "--seed", "-s",
                        help="The random seed to be used for the simulation",
                        default=SEED, type=int)
    parser.add_argument("OB", "-ob", "--output_buffer",
                        help="The size of the output buffer at the server side, in Megabits",
                        default=OB, type=int)
    parser.add_argument("IAT", "-i", "--inter_arrival_time",
                        help="Interarrival time (1 over lambda), in seconds"
                        default=INTER_ARRIVAL_TIME, type=float)
    parser.add_argument("DURATION", "-d", "--duration",
                        help="Mean duration of the videos, in seconds",
                        default=DURATION, type=float)
    parser.add_argument("WAIT_TIME", "-w", "--wait_time",
                        help="The time a customer wait with the player stuck before going away",
                        default=WAIT_TIME, type=float)
    parser.add_argument("SERV_SPEED", "-us", "--upload_speed",
                        help="The access speed on the network channel at the server side, in Megabits per second",
                        default=SERV_SPEED, type=int)
    parser.add_argument("CLI_SPEED", "-ds", "--download_speed",
                        help="The access speed on the network channel at the client side, in Megabits per second",
                        default=CLI_SPEED, type=float)
    parser.add_argument("RUN_TIME", "-T", "--simulation_time",
                        help="The duration of the simulation, in simulation seconds (not real time)",
                        default=RUN_TIME, type=int)
    args = parser.parse_args()
    
    random.seed(args.SEED)
    env = simpy.Environment()
    network = Network(args.RTT, env)
    server = Server(network, args.S, args.SERV_SPEED, args.OB, env)
    clientspawn = ClientSpawner(args.IAT, args.DURATION, args.WAIT_TIME,
                                network, server)
    env.process(clientspawn.run(env))
    env.run(args.RUN_TIME)
    plt.figure()
    plt.plot(server.time, server.buf_sz)
    plt.figure()
    plt.plot(server.time_clients, server.nclients)
    plt.show()


if __name__ == '__main__':
    main()
