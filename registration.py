#!/usr/bin/python3
# Code from https://github.com/jonogreenz/py-pushover-open-client

import argparse

from pushover_open_client import Client

def deviceSetup(deviceName, config):
    # Setup with a base config containing email and password
    client = Client(config)

    # Logs into Pushover's servers based on config
    client.login()

    # Registers a new device using the supplied device name
    client.registerDevice(deviceName)

    # Save the new device to a new config so registration
    # can be bypassed in the future
    client.writeConfig(config)

def main():
    parser = argparse.ArgumentParser(description='Set device name')
    parser.add_argument('device_name',
                    help='The desired name under which to register the device')
    parser.add_argument('--cfg', dest='config', default="test.json",
                    help='JSON file configured for registration')

    args = parser.parse_args()

    deviceSetup(args.device_name, args.config)

if __name__ == "__main__":
    main()
