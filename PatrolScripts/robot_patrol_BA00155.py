#!/usr/bin/env python3
"""
robotpatrol.py
Script for handling a robot on patrol

Aditya Earanky

Copyright (c) Ava Robotics Inc. 2020, All Rights Reserved.
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

	# print("\nPlease enter the following details to get a list of tags")
	print("--------------------------------------------------------")

	# RMS = input("RMS (Example: swtest.ava8.net): ")
	# ID = input("Robot's ID: ")
	# UN = input("Username: ")
	# PS = getpass("Password: ")

	RMS = "eft.ava8.net"
	ID = "BA00155"
	UN = "mitgbfb"
	PS = "mitgbfb2020"

	print('\nConnecting to robot ',ID,' for patrol.')

	# TODO: configure local server to not rely on wifi dropouts

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

	# listoftags = ["a_1", "a_12", "a_2", "b_3", "b_34", "b_4", "b_1", "b_2", "b_3", "b_4", "c_1", "c_2", "d_3", "d_4", "d_1", "d_2"]

	listoftags = ["a_1", "a_2", "b_3", "b_4", "b_1", "b_2", "c_3", "c_4", "c_1", "c_2", "d_3", "d_4", "d_1", "d_2", "e_3", "e_4"]

	listoftags = ["d_1", "d_2", "d_3", "d_4"]

	# check and re-enter tag names till they are correct
	wrongtags = 0
	for tagi in listoftags:
		if not (tagi in dic):
			print('\nThe tag ',tagi, 'is not a valid tag.')
			wrongtags = wrongtags + 1
	if wrongtags > 0:
		print('\nThe patrol route contained invalid tags. Please check from the list of tags:')
		print("\n-------------  TAGS  ---------------------")
		for key, values in dic.items():
			print(key)
		print("----------------------------------")
		# get a correct list for the robot
		listoftags = []
		("\nPlease re-enter the list: ")
		listlength = int(input("\nEnter the total number of tags: "))			
		# iterate
		for i in range(0,listlength):
			while True:
				tag_i = input("Tag {} of {}: ".format(i+1,listlength))
				if not (tag_i in dic):
					print('\nPlease choose a tag from the list displayed above.\n')
					time.sleep(1.0)
				else:
					break
			listoftags.append(tag_i)

	print("--------------------------------------------")
	print("\nThe tags to patrol are: \n")
	print(*listoftags, sep = ", ")  
	print("---------------------------------------------")
 
	duration = .1
	sys.stdout.write("\nPerforming a single patrol route of Tags")
	duration_in_secs = float(duration) * 3600

	# set the patrol log file name
	cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
	filename='{} - Patrol Test Results - {}.txt'.format(ID.upper(),cur_time)

	# set variables before starting the patrol
	count = 1
	timespent = 0.0
	starttime = time.time()

	with StdoutTee(filename, buff=1):

		sys.stdout.write("\nStarted patrol")
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
		sys.stdout.write("\nCompleted patroling for {} hours, and completed a total of {} iterations\n\n".format(duration, count-1))

		#dock robot after patrol 
		sys.stdout.write("\nReturning to dock.")
		utils.dockRobot()

if __name__ == '__main__':
	main()