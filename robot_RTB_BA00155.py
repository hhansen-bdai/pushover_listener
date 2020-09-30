#!/usr/bin/env python3
"""
robotpatrol.py
Script for handling a robot on patrol

Aditya Earanky

Copyright (c) Ava Robotics Inc. 2020, All Rights Reserved.
"""

import time
import sys
import PatrolScripts.robotutils as robotutils
import logging
import datetime
from datetime import date
from getpass import getpass
from tee import StdoutTee


# Additional UVC control code
from arduino_comm import Messenger


logger = logging.getLogger(__name__)

BATTERY_CHECK_INTERVAL = 180

lowBatteryPct = 20.0
highBatteryPct = 97.0

# Sometimes the robot does not report charge level. Utils returns "-1" in this case.
# Set it to a safe value, so everything continues as normal assuming the robot responds
# again with the correct value soon.
def getChargeLevelSafe(utils):
    level = utils.getBatteryCharge()
    if level == "-1":
        level = lowBatteryPct + 0.1
    else:
        level = float(level)
    return level


def main():

    # This HTTP requests logger will be over-written everytime this script runs from the start
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p', filename='requests_logfile.txt', filemode='w', level=logging.DEBUG)

    # print("\nPlease enter the following details to get a list of tags")
    print("--------------------------------------------------------")

    # RMS = input("RMS (Example: swtest.ava8.net): ")
    # ID = input("Robot's ID: ")
    # UN = input("Username: ")
    # PS = getpass("Password: ")

    RMS = "base.ava8.net"
    ID = "BA00155"
    UN = "mitgbfb"
    PS = "ap123"

    print('\nConnecting to robot ',ID,' for patrol.')

    # TODO: configure local server to not rely on wifi dropouts

    utils = robotutils.RobotUtils(RMS,UN,PS,ID)

    # get current charge and set charge_complete accordingly
    cur_charge = getChargeLevelSafe(utils)
    charge_complete = False
    if cur_charge > lowBatteryPct:
        charge_complete = True

    

    listoftags = []

    
 
    duration = .1
    sys.stdout.write("\nReturning to Base")
    duration_in_secs = float(duration) * 3600

    # set the patrol log file name
    cur_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename='{}_RTB_{}.txt'.format(ID.upper(),cur_time)

    # set variables before starting the patrol
    count = 1
    timespent = 0.0
    starttime = time.time()


    # Define the UVC Lights
    UVCLights = Messenger(None,None,None) #remote ip, port, host ip
    UVCLights.ip = "172.18.0.50"
    UVCLights.port = 8888
    UVCLights.host = "172.18.0.1"

    with StdoutTee(filename, buff=1):

        lightson = input("Turn on UVC Lights? (Y/N)")
        if lightson == 'Y' or lightson == 'y':
            print('\nTurning on UVC Lights')
            UVCLights.beginUVCLights()
        else:
            UVCLights.stopUVCLights()
            print('\n Okay, no UVC Lights')

        sys.stdout.write("\n--------------")

        while(timespent < duration_in_secs and count < 2):

            # calculate time spent
            now = time.time()
            timespent = now - starttime

            # if charging is not complete, check if overall time spent exceeded duration. If it did, stop patroling.
            # Otherwise, check current charge. If it's greater than highBatteryPct, set charging is complete,
            # else sleep for BATTERY_CHECK_INTERVAL. 
            if (not charge_complete):
                if (timespent > duration_in_secs):
                    sys.stdout.write("\nExiting patrol while charging.")
                    break

                cur_charge = getChargeLevelSafe(utils)
                if (cur_charge > highBatteryPct):
                    charge_complete = True
                else:
                    time.sleep(BATTERY_CHECK_INTERVAL)

                # if charging is still not complete, continue to check in the next loop.
                if (not charge_complete):
                    continue

            # patrol only when we have enough charge or when charging is complete
            if (cur_charge > lowBatteryPct):
                
                # Patrol the set of tags in a list
                for tagi in listoftags:

                    cur_time = cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sys.stdout.write("\nIteration {} - {} - Driving to {}".format(count, cur_time, tagi))

                    # drive to tag ii
                    state = utils.driveRobotToTag(dic[tagi])
                    utils.waitOnComplete()

                    # check battery status
                    # get current charge and if there isn't enough, set charge_complete to False and return to dock
                    cur_charge = getChargeLevelSafe(utils)
                    if (cur_charge < lowBatteryPct):
                        charge_complete = False
                        sys.stdout.write("\nReturning to dock after " + str(count-1) + " rounds")
                        count = count + 1
                        utils.dockRobot()

                    
            # increase lap count
            count = count + 1

            # get current charge and if there isn't enough, set charge_complete to False and return to dock
            cur_charge = getChargeLevelSafe(utils)
            if (cur_charge < lowBatteryPct):
                charge_complete = False
                sys.stdout.write("\nReturning to dock after " + str(count-1) + " rounds")
                utils.dockRobot()

        sys.stdout.write("\nCompleted patrol")
        sys.stdout.write("\n----------------")
        sys.stdout.write("\nCompleted patrolling for {} hours, and completed a total of {} iterations\n\n".format(duration, count-1))

        # turn off UVC lights
        if lightson == 'Y' or lightson == 'y':
            print('\nTurning off UVC Lights')
            UVCLights.stopUVCLights()

        #dock robot after patrol 
        sys.stdout.write("\nReturning to dock.")
        utils.dockRobot()

if __name__ == '__main__':
    main()