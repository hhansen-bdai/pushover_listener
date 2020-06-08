#!/usr/bin/python3
# Code from https://github.com/jonogreenz/py-pushover-open-client

from pushover_open_client import Client

class ReyClient(object):

    def __init__(self, client):
        self.client = client

    def getOutstandingMessages(self):
        return self.client.getOutstandingMessages()

    def openSocket(self):
        self.client.getWebSocketMessages(self.messageCallback)

    def shutDownLights(self):
        # STUB: Shut down uv lights through 
        # Arduino
        pass

    def goHome(self):
        # STUB: Send AVA base back to dock
        pass

    def setUpArduino(self):
        # STUB: Set up arduino for UV patrol
        pass

    def messageCallback(self, messageList):
    #Prcoess/do work with messageList!
        if(messageList):
            for message in messageList:
                #Do work with message here!
                print("#{}\n{}\n{}".format(message.id, message.title, message.message))
                if "GBFB Building now DISARMED" in message.title or \
                    "GBFB Building Status in ALARM" in message.title:
                        print('Fake emergency shut off initiated')
                        print('Fake shutting off the arduino now...')
                        self.shutDownLights()
                        self.goHome()
                        print('Fake shut off completed')

                elif "GBFB Building now ARMED" in message.title and \
                    "GBFB Building Status Alarm CLEARED" in message.title:
                        print('Fake resuming normal operations')
                        print('Fake setting up arduino now...')
                        self.setUpArduino()
                        print('Fake set up completed')

                #Make sure to acknowledge messages with priority >= 2
                if(message.priority >= 2):
                    if(message.acked != 1):
                        self.client.acknowledgeEmergency(message.receipt)	
                #Make sure you delete messages that you recieve!
                self.client.deleteMessages(messageList[-1].id)

def main():

    # Setups with a device configuration
    client = ReyClient(Client("../.secrets/config.json"))

    # Get any messages sent before the client has started
    messageList = client.getOutstandingMessages()

    # Pass our function as a parameter, this will run 'forever'
    client.openSocket()

if __name__ == "__main__":
    main()
