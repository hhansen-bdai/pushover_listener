#!/usr/bin/env python3

import socket
import time
from builtins import bytes

# Initial parameters
UDP_IP = "172.18.0.50"
UDP_PORT = 8888
begin_lights = bytes(b"b")
stop_lights = bytes(b"s")


# get the duration as an input
time.sleep(1.0)
duration = input("\nPlease enter the duration for the lights (in minutes): ")
duration_in_secs = float(duration) * 60


# Turn on the lights
print("\nTurning on UVC lights for ",duration," minutes")
print("\n--------------")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(begin_lights, (UDP_IP, UDP_PORT))


time.sleep(duration_in_secs)

# Turn off the lights

sock.sendto(stop_lights, (UDP_IP, UDP_PORT))
print("\nUVC lights are now off")
print("\n--------------")