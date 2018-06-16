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
K = 10  # Number of packets in the client buffer
RTT = 0.5
OB = 500  # Mb Output buffer capacity of the server
MAX_QUALITY = 5
INTER_ARRIVAL_TIME = 1  # Seconds
DURATION = 100  # Seconds
WAIT_TIME = 5  # Seconds
WAIT_TIME_START = S*K
SERV_SPEED = 10000  # Mbps
CLI_SPEED = 3  # Mbps
RUN_TIME = 1000
SEED = 12


class ClientSpawner(object):
    """Documentation for ClientSpawner

    """
    def __init__(self, S, K, inter_arrival_time, cli_speed, duration,
                 wait_time, network, server):
        super(ClientSpawner, self).__init__()
        self.inter_arrival_time = inter_arrival_time
        self.duration = duration
        self.wait_time = wait_time
        self.network = network
        self.server = server
        self.cli_speed = cli_speed
        self.S = S
        self.K = K

    def run(self, env):
        self.count = 0
        while True:
            duration = random.normalvariate(self.duration, 0)
            duration -= duration % S
            wait_time = random.expovariate(1.0/self.wait_time)
            client = Client(self.S, self.K, self.server, self.network, env,
                            MAX_QUALITY, self.cli_speed, duration,
                            wait_time, self.count, WAIT_TIME_START)
            env.process(client.run())
            self.count += 1
            yield env.timeout(random.expovariate(1.0/self.inter_arrival_time))


def main():
    parser = ArgumentParser()
    #     -----------      PARAMETERS OF THE SIMULATION      -----------      #
    parser.add_argument("-S",
                        help="The duration of a fragment of video, in seconds",
                        default=S, type=float)
    parser.add_argument("-k",
                        help="The length of the client buffer, " +
                        "in number of fragments", default=K, type=int)
    parser.add_argument("--rtt", "-R",
                        help="The round trip time between server " +
                        "and client, in seconds", default=RTT, type=float)
    parser.add_argument("--seed", "-s",
                        help="The random seed to be used for the simulation",
                        default=SEED, type=int)
    parser.add_argument("-ob", "--output_buffer",
                        help="The size of the output buffer at the " +
                        "server side, in Megabits", default=OB, type=int)
    parser.add_argument("-i", "--inter_arrival_time",
                        help="Interarrival time (1 over lambda), in seconds",
                        default=INTER_ARRIVAL_TIME, type=float)
    parser.add_argument("-d", "--duration",
                        help="Mean duration of the videos, in seconds",
                        default=DURATION, type=float)
    parser.add_argument("-w", "--wait_time",
                        help="The time a customer wait with the player " +
                        "stuck before going away",
                        default=WAIT_TIME, type=float)
    parser.add_argument("-us", "--upload_speed",
                        help="The access speed on the network channel at " +
                        "the server side, in Megabits per second",
                        default=SERV_SPEED, type=int)
    parser.add_argument("-ds", "--download_speed",
                        help="The access speed on the network channel at " +
                        "the client side, in Megabits per second",
                        default=CLI_SPEED, type=float)
    parser.add_argument("-T", "--simulation_time",
                        help="The duration of the simulation, in " +
                        "simulation seconds (not real time)",
                        default=RUN_TIME, type=int)
    #      ---------------      OUTPUT OPTIONS      ---------------      #
    parser.add_argument("--plot_server_buf",
                        help="Name of the file on which the server " +
                        "buffer size over time will be plot. If this is not " +
                        "set, the plot will not be produced")
    parser.add_argument("--plot_number_of_clients",
                        help="Name of the file on which the number of " +
                        "clients over time will be plot. If it is not set, " +
                        "the plot will not be produced")
    parser.add_argument("--print_total_customers", "-pt", help="Print the " +
                        "total number of customer that has been produced by " +
                        "the spawning process.", action="store_true")
    parser.add_argument("--print_churns", "-pc", help="Print the " +
                        "number of clients that left the service before the " +
                        "end of the video", action="store_true")
    parser.add_argument("--print_successful", "-ps", help="Print the " +
                        "number of clients that were successfully served by " +
                        "the system", action="store_true")
    parser.add_argument("--print_parameters", "-pp", help="Print the " +
                        "simulation parameters", action="store_true")
    parser.add_argument("-o", "--output_file", help="Specify that the " +
                        "output should be written on the provided file " +
                        "instead of the standard output")
    parser.add_argument("-a", "--append_to_file", help="Specify that the " +
                        "output should be appended on the provided file " +
                        "instead of the standard output")
    args = parser.parse_args()

    random.seed(args.seed)
    env = simpy.Environment()
    env.churns = 0
    env.churns_start = 0
    env.success = 0
    network = Network(args.rtt, env)
    server = Server(network, args.S, args.upload_speed,
                    args.output_buffer, env)
    clientspawn = ClientSpawner(args.S, args.k, args.inter_arrival_time,
                                args.download_speed, args.duration,
                                args.wait_time, network, server)
    env.process(clientspawn.run(env))
    env.run(args.simulation_time)
    if args.plot_server_buf is not None:
        plt.figure()
        plt.plot(server.time, server.buf_sz)
        plt.savefig(args.plot_server_buf)
    if args.plot_number_of_clients is not None:
        plt.figure()
        plt.plot(server.time_clients, server.nclients)
        plt.savefig(args.plot_number_of_clients)
    to_print = []
    if args.print_parameters:
        to_print.append([args.seed, args.S, args.k, args.inter_arrival_time, args.download_speed,
                         args.duration, args.wait_time, args.rtt, args.upload_speed, args.output_buffer])
    if args.print_total_customers:
        to_print.append(clientspawn.count)
    if args.print_successful:
        to_print.append(env.success)
    if args.print_churns:
        to_print.append(env.churns)
        to_print.append(env.churns_start)
    if args.output_file is not None:
        of = open(args.output_file, "w")
        of.write(str(to_print))
    elif args.append_to_file is not None:
        of = open(args.append_to_file, "a")
        of.write(str(to_print))
    else:
        print(to_print)


if __name__ == '__main__':
    main()
