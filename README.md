This is a repository for the GBFB UV Robot 
emergency shutoff system, built on the 
pushover service and API (https://pushover.net/)
and the wonderful Python library for it by 
jonogreenz (https://github.com/jonogreenz/py-pushover-open-client)

In order to use this repo, a person must download it
in the typical fashion, fill the config.json file with
their information where they have been filled in with
examples, and leaving blank the blank fields. Then run
registration.py with your desired device name. After this,
listener.py should process for incoming messages to that 
device for as long as it's running
