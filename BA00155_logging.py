
import time
import sys
import PatrolScripts.robotutils as robotutils
import logging
import datetime
from datetime import date
from getpass import getpass
from tee import StdoutTee


def getChargeLevelSafe(utils):
    level = utils.getBatteryCharge()
    if level == "-1":
        level = lowBatteryPct + 0.1
    else:
        level = float(level)
    return level


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


    print('\nConnecting to robot ',ID,' for logging position.')

    # TODO: configure local server to not rely on wifi dropouts

    utils = robotutils.RobotUtils(RMS,UN,PS,ID)

    # set the patrol log file name
    cur_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename='{}_TrajHist_{}.txt'.format(ID.upper(),cur_time)
    starttime = time.time()

    with StdoutTee(filename, buff=1):

        sys.stdout.write("\nTrajectory History")
        sys.stdout.write("\n--------------")
        while True:
            now = time.time()
            timespent = now - starttime
            try:
                coord = utils.curRobotPosition()
                # coord is a dict, add time and save
                coord['Time'] = now
                sys.stdout.write("\n{}".format(coord))
            time.sleep(0.5)
       



if __name__ == '__main__':
    main()