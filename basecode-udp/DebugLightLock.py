import socket

UDP_IP_host = "172.18.0.1"
UDP_IP_remote = "172.18.0.50"
UDP_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP_host, UDP_PORT))


count = 1

while True:
	sock.sendto(b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", (UDP_IP_remote, UDP_PORT))
	data, addr = sock.recvfrom(1024)
	print("Message count: % s" % count)
	print("Received message: % s" % data)
	count = count + 1
