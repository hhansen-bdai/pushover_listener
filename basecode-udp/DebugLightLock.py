#!/usr/bin/env python3

# Script to check if the base can send and receive messages from the board


import socket
from builtins import bytes
import select


UDP_IP_host = "172.18.0.1"
UDP_IP_remote = "172.18.0.50"
UDP_PORT = 8888

# # #check it out locally
# UDP_IP_remote = "127.0.0.1"
# UDP_IP_host = "127.0.0.1"


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP_host, UDP_PORT))

sock.settimeout(1)

test_message = bytes(b"testing123")


print("Testing message passing between base and relay board.")

sent = 1
count = 1
received = 0



while received == 0:
        print("Message count: % s" % count)
        sent = sent + 1
        sock.sendto(test_message, (UDP_IP_remote, UDP_PORT))
        try:
            data, addr = sock.recvfrom(1024)
            data = data.decode()
            if data[0]:
                print("Received message: {}".format(data))
                received = 1
                break
        except:
            print("No message received")
        count = count + 1