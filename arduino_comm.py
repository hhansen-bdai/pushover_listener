import socket

class Messenger(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def stopUVCLights(self):
        Message = b"s"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def beginUVCLights(self):
        Message = b"b"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))