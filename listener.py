#!/usr/bin/python3
# Code from https://github.com/jonogreenz/py-pushover-open-client

from pushover_open_client import Client

def messageCallback(messageList):
#Prcoess/do work with messageList!
    if(messageList):
        for message in messageList:
            #Do work with message here!
            print("#{}\n{}\n{}".format(message.id, message.title, message.message))
            if "EMERGENCY" in message.message:
                print('Emergency shut off initiated')
                print('Shutting off the arduino now...')
                print('Shut off completed')

            #Make sure to acknowledge messages with priority >= 2
            if(message.priority >= 2):
                if(message.acked != 1):
                    client.acknowledgeEmergency(message.receipt)	
        #Make sure you delete messages that you recieve!
        client.deleteMessages(messageList[-1].id)

def main():

    # Setups with a device configuration
    client = Client("config.json")

    # Get any messages sent before the client has started
    messageList = client.getOutstandingMessages()

    if(messageList):
        client.deleteMessages(messageList[-1].id)

    # Pass our function as a parameter, this will run 'forever'
    client.getWebSocketMessages(messageCallback)

if __name__ == "__main__":
    main()
