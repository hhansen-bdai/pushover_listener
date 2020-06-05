
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8888
Message = b"Hello there!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(Message, (UDP_IP, UDP_PORT))

