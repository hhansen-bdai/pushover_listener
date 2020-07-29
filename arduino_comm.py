import socket

class Messenger(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def stopUVCLights(self):
        # turn off the UVC lights
        Message = b"s"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def beginUVCLights(self):
        # turn on the UVC lights
        Message = b"b"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def testRelayComm(self):
        # board lights will flash fancy colors to confirm communication
        Message = b("t")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def resetRelayBoard(self):
        # resets board
        Message = b("r")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))