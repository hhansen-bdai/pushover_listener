import socket
from builtins import bytes


class Messenger(object):
    def __init__(self, ip, host, port):
        self.ip  = ip
        self.host = host
        self.port = port

    def stopUVCLights(self):
        # turn off the UVC lights
        Message = bytes(b"s")
        
        # Keep sending command until lights turn off
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        sock.settimeout(1) #non-blocking mode

        # debug values
        sent = 1
        count = 1
        received = 0

        while received == 0:
            print("Message count: % s" % count)
            sent = sent + 1
            sock.sendto(Message, (self.ip, self.port))
            try:
                data, addr = sock.recvfrom(1024)
                data = data.decode()
                if data[0]:
                    print("Received message: {}".format(data))
                    received = 1
                    break
            except:
                print("No message received, trying again")
                count = count + 1


    def beginUVCLights(self):
        # turn on the UVC lights
        Message = bytes(b"b")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def testRelayComm(self):
        # board lights will flash fancy colors to confirm communication
        Message = bytes(b"t")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))

    def resetRelayBoard(self):
        # resets board
        Message = bytes(b"r")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(Message, (self.ip, self.port))