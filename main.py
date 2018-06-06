#!/usr/bin/python3
import simpy
from client import Client
from network import Network
from server import Server

# The client will download K packets before starting
# the player
# REMEMBER: waiting time is related to network speed, not
# to video to play
S = 5 # Duration of the video contained in a packet
K = 12 # Number of packets in the client buffer
RTT = 5
OB = 10000 # Mb Output buffer capacity of the server

def main():
    env = simpy.Environment()
    network = Network(RTT, env)
    server = Server(network, S, OB, env)
    client = Client(S, K, server, network, env, 4, 2000, 1)
    env.process(client.run())
    env.run()
    
if __name__ == '__main__':
    main()
