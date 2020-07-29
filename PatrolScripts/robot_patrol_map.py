#!/usr/bin/env python3
"""
robotpatrol.py
Script for handling a robot on patrol

Aditya Earanky

Copyright © Ava Robotics Inc. 2020, All Rights Reserved.
"""

import time
import sys
import robotutils
import logging
import datetime
from datetime import date
from getpass import getpass
from tee import StdoutTee

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

	print("\nPlease enter the following details to get a list of tags")
	print("--------------------------------------------------------")

	RMS = input("RMS (Example: swtest.ava8.net): ")
	ID = input("Robot's ID: ")
	UN = input("Username: ")
	PS = getpass("Password: ")

	utils = robotutils.RobotUtils(RMS,UN,PS,ID)

	# get current charge and set charge_complete accordingly
	cur_charge = getChargeLevelSafe(utils)
	charge_complete = False
	if cur_charge > lowBatteryPct:
		charge_complete = True

	# get a dictionary of tags
	time.sleep(1.0)
	print("\nRetrieving tags now.")
	dic = {}
	tagList = utils.getTagList()

	# if there are no tags to be found, exit
	if (tagList == None):
		print('\nNo tags were found. Either check the credentials entered, if there are any ' +
			'tags in the map, or if the robot is connected to the correct rms. Exiting program.\n')
		time.sleep(10.0)
		exit()

	for key, values in tagList.items():
		dic[values["name"].lower()] = key

	# print list of tags and choose two of them
	print("\n-------------  TAGS  ---------------------")
	for key, values in dic.items():
		print(key)
	print("--------------------------------------------")
	print("\nChoose two tags from the list displayed above")
	print("---------------------------------------------")

	# check and re-enter tag names till they are correct
	while True:
		tag1 = input("First tag: ")
		if not (tag1 in dic):
			print('\nPlease choose a tag from the list displayed above.\n')
			time.sleep(1.0)
		else:
			break

	while True:
		tag2 = input("Second tag: ")
		if not (tag2 in dic):
			print('\nPlease choose a tag from the list displayed above.\n')
			time.sleep(1.0)
		else:
			break

	# get the duration
	time.sleep(1.0)
	duration = input("\nPlease enter the desired Patrol duration (in hours): ")
	duration_in_secs = float(duration) * 3600

	# set the patrol log file name
	cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
	filename='{} - Patrol Test Results - Duration {} - {}.txt'.format(ID.upper(), duration, cur_time)

	# set variables before starting the patrol
	count = 1
	timespent = 0.0
	starttime = time.time()

	with StdoutTee(filename, buff=1):

		sys.stdout.write("\nStarted patrol")
		sys.stdout.write("\n--------------")

		while(timespent < duration_in_secs):

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
				cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				sys.stdout.write("\nIteration {} - {} - Driving to {}".format(count, cur_time, tag1))

				# drive to tag 1
				state = utils.driveRobotToTag(dic[tag1])
				utils.waitOnComplete()

				# increase lap count
				count = count + 1

				cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				sys.stdout.write("\nIteration {} - {} - Driving to {}".format(count, cur_time, tag2))

				# drive to tag 2
				state = utils.driveRobotToTag(dic[tag2])
				utils.waitOnComplete()

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
		sys.stdout.write("\nCompleted patroling for {} hours, and completed a total of {} iterations\n\n".format(duration, count-1))

		#dock robot after patrol 
		sys.stdout.write("\nReturning to dock.")
		utils.dockRobot()

if __name__ == '__main__':
	main()