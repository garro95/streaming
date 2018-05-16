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

def main():
    network = Network(RTT)
    client = Client(S, K)
    
if __name__ == '__main__':
    main()
