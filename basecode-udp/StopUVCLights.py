
import socket

UDP_IP = "172.18.0.50"
UDP_PORT = 8888
Message = b"s"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(Message, (UDP_IP, UDP_PORT))

