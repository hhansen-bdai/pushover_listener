#!/usr/bin/env python3

import socket
from builtins import bytes


UDP_IP = "172.18.0.50"
UDP_PORT = 8888
Message = bytes(b"t")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(Message, (UDP_IP, UDP_PORT))

