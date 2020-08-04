#!/usr/bin/python
# Code from https://github.com/jonogreenz/py-pushover-open-client

from pushover_open_client import Client
from arduino_comm import Messenger

class ReyClient(object):

    def __init__(self, client):
        self.client = client
        self.messenger = Messenger(None, None)

    def getOutstandingMessages(self):
        return self.client.getOutstandingMessages()

    def openSocket(self):
        self.client.getWebSocketMessages(self.messageCallback)

    def messageCallback(self, messageList):
    #Prcoess/do work with messageList!
        if(messageList):
            for message in messageList:
                #Do work with message here!
                print("#{}\n{}\n{}".format(message.id, message.title, message.message))
                if "GBFB Building now DISARMED" in message.title or \
                    "GBFB Building Status in ALARM" in message.title:
                        print('Shut off initiated')
                        print('Shutting off lights now...')
                        self.messenger.stopUVCLights()
                        print('Shut off completed')

                # elif "GBFB Building now ARMED" in message.title and \
                #     "GBFB Building Status Alarm CLEARED" in message.title:
                #         print('Resuming normal operations')
                #         print('Setting up lights now...')
                #         self.messenger.beginUVCLights()
                #         print('Set up completed')

                #Make sure to acknowledge messages with priority >= 2
                if(message.priority >= 2):
                    if(message.acked != 1):
                        self.client.acknowledgeEmergency(message.receipt)	
                #Make sure you delete messages that you recieve!
                self.client.deleteMessages(messageList[-1].id)

def main():

    # Setups with a device configuration
    client = ReyClient(Client("../.secrets/config.json"))

    # ISet Messenger member to correct ip and port
    client.messenger.ip = "172.18.0.50" # remote ip (where to send messages)
    client.messenger.port = 8888
    client.messenger.host = "172.18.0.1" #host ip (where to listen)

    # Get any messages sent before the client has started
    messageList = client.getOutstandingMessages()

    # Pass our function as a parameter, this will run 'forever'
    client.openSocket()

if __name__ == "__main__":
    main()
