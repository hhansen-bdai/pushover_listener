# -*- coding: utf-8 -*-
"""
Utility class for using Ava robot API

@author: Danish
@author: Mark Duckworth - updating for robot patrol application
@author: Aditya Earanky
Copyright © Ava Robotics Inc. 2020, All Rights Reserved.
"""

import json           # for encoding POST arguments
import math           # for PI
import sys            # for flush & timestamping capabilty
import time           # for timestamping and sleep functionality
from urllib import request,error    # for the authenticated connection
import requests
from time import strftime, localtime # for timestamping
import base64
import ssl
import logging
from requests.auth import HTTPBasicAuth

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

logger = logging.getLogger(__name__)

class RobotUtils:
    def __init__(self, RMS, UN, PS, RobotID):
        self.setArgumentPassedValue(RMS, UN, PS,RobotID)
        # self.logFile =  sys.argv[0][0:-3]+"_"+self.robot + "_"+strftime("%m-%d-%Y_%H%M", localtime())+".log"
        self.setBaseCode()
        self.inPatrol = False
        self.ready = False


    def setArgumentPassedValue(self, RMS, UN, PS, RobotID):

        self.uid = UN
        self.pwd = PS
        self.host = RMS
        self.robot = RobotID.upper()
        self.ip = None

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Function:  msgDebug
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def msgDebug(self, *args):
        logstr = self.makeMsgString(args)
        logger.debug("DEBUG: " + logstr)

    def msgInfo(self, *args):
        logstr = self.makeMsgString(args)
        logger.info("INFO: " + logstr)
    
    def msgWarn(self, *args):
        logstr = self.makeMsgString(args)
        logger.warn("WARN: " + logstr)
    
    def msgError(self, *args):
        logstr = self.makeMsgString(args)
        logger.error(logstr)

    def makeMsgString(self, *args):
        output = ' '.join(map(str,args))
        logstr = "{} {}".format(self.robot, output)
        return logstr
        
    def setBaseCode(self):
        base64string = '%s:%s' % (self.uid, self.pwd)
        self.base64string = base64.b64encode(bytes(base64string, "utf-8")).decode('ASCII')
        self.msgDebug(self.base64string)

    ###############################################################################
    ### Function:  getCommand
    ###
    ### Does HTTP GET for the given URI
    ### - opens the URL, posts data, and gets the response
    ### - returns the contents of the response
    ### - If an error is encountered, this
    ###############################################################################
    def getCommand(self, commandURI):
        sys.stdout.flush()
        url = None
        try:
            if not self.ip:
                url = "https://"+self.host+"/api/htproxy/WebDrive/"+self.robot+'/'+commandURI
            else:
                url = "http://"+self.ip+":8800"+commandURI

            res = requests.get(url, auth=(self.uid, self.pwd))

            return res.text

        except requests.exceptions.HTTPError as e:
            if e.code == 404:
                self.msgError(self.robot+" is Not Found in Host :"+self.host)
                sys.exit(1)
            elif e.code == 500:
                self.msgError(self.robot+" is Disconnected in Host :"+self.host)
                sys.exit(1)
            else:
                self.msgError("Invalid credential")
                sys.exit(1)

        except requests.exceptions.Timeout:
                currentTime = self.timeStamp()
                self.msgError(currentTime + " - Connection timeout.")

        except Exception as e:
            self.msgError(url)
            self.msgError("Unable to perform HTTP Get. %s"%repr(e))
            self.msgError("Please Check if Robot is connected In RMS : command " + commandURI)
            return None

    ###############################################################################
    ### Function:  postCommand
    ###
    ### Does HTTP POST for the given URI
    ### - opens the URL, posts data, and gets the response
    ### - returns the contents of the response
    ### - If an error is encountered, this
    ###############################################################################
    def postCommand(self,commandURI, argDict=None):

        try:
            postData=json.dumps(argDict)
        except:
            postData = None
        try:
            if not self.ip:
                url = "https://"+self.host+"/api/htproxy/WebDrive/"+self.robot+'/'+commandURI
            else:
                url = "http://"+self.ip+"/"+commandURI

            res = requests.post(url, data=postData, auth=(self.uid, self.pwd))

        except requests.exceptions.HTTPError as e:
            if e.code == 404:
                self.msgError(self.robot+" is Not Found in Host :"+self.host)
                sys.exit(1)
            elif e.code == 500:
                self.msgError(self.robot+" is Disconnected in Host :"+self.host)
                sys.exit(1)
            else:
                self.msgError("Invalid credential")
                sys.exit(1)

        except requests.exceptions.Timeout:
            currentTime = self.timeStamp()
            self.msgError(currentTime + " - Connection timeout.")

        except Exception as e:
            currentTime = self.timeStamp()
            self.msgError(currentTime + " - Error posting command to robot. %s"%repr(e) )
            return None

    def dial(self, number):
        self.getCommand("/robot/tel/dial?number=" + number)
        return None

    def hangUp(self):
        return self.getCommand('/robot/tel/hangup')


    def timeStamp(self):
        testTime = strftime("%m-%d-%Y %H%M%S", localtime())
        return testTime

    def curRobotPosition(self):
        robotPositionData = json.loads(self.getCommand('/robot/drive/position'))
        return (robotPositionData)

    def robotPositionValid(self):
        robotPositionData = self.curRobotPosition()
        return (robotPositionData["positionValid"])

    def getTestMapId(self):
        return self.getConfigData("testMap")

    def getCurrentRobotMap (self):
        try:
            retVal = json.loads(self.getRobotMapInfo ())
            retVal = retVal["currentDbFile"]
        except Exception as e:
            s=repr(e)
            self.msgError("getCurrentRobotMap failed:", s)
            sys.stdout.flush()
            retVal="INVALID"
            raise
        return retVal

    def getVolume(self):
        volume = json.loads(self.getCommand('/robot/settings/get/tel/volume'))
        vol = volume['value']
        return int(vol)

    def setVolume(self, vol):
        self.getCommand("/robot/settings/set/tel/volume?value="+str(vol))
        return None

    ##############################################################################
    ### Function:  getBatteryCharged
    ###
    ### Checks the current percentage of the battery, returned as "XX.XX"
    ###
    ### Returns:
    ###   Battery percentage, example "50.10"
    ###   "-1" if the robot does not provide a charge level
    ###
    ##############################################################################
    def getBatteryCharge(self):
        
        try:
            API = "/robot/health"
            retValS = self.getCommand(API)
            retVal = json.loads(retValS)
            retString = retVal["batteryCharge"]
        except Exception as e:
            if not (retValS == None):
                self.msgError("getBatteryCharge() " + retValS)
            else:
                self.msgError("getBatteryCharge() failed in getCommand()")
            retString = "-1"
        self.msgDebug("getBatteryCharge() " + retString)    
        return retString
        

    ###############################################################################
    ### Function:  getState
    ###
    ###   Retrieves data from robot's runningBehaviorState (text) field, the big
    ###   problem with the State is it goes to "Idle" when robot stopped, but the
    ###   reason is not displayed (completed, cancelled, etc.).
    ###############################################################################
    def getState(self):
        retState = "Wait"
        state = self.getCommand('/robot/navigation/runningBehaviorState')
        if state != None:
            state = json.loads(state)
            retState = state["text"]
        self.msgDebug("getState " + retState)
        return (retState)

    ###############################################################################
    ### Function:  getStatus
    ###
    ###   Retrieves the data from the robot's updates planStatus field.  This
    ###   command returns more specific information on why robot command has
    ###   stopped (completed, cancelled, etc.).
    ###############################################################################
    def getStatus(self):
        retStatus = "Wait"
        state = self.getCommand('/robot/drive/updates')
        if state != None:
            state = json.loads(state)
            retStatus = state["planStatus"]
        self.msgDebug("getStatus " + retStatus)
        return (retStatus)

    ###############################################################################
    ### Function:  goToStatus
    ###
    ###############################################################################
    def goToStatus(self):
        status = self.getCommand('/robot/tel/goToStatus')
        status = json.loads(status)
        self.msgDebug("{} goToStatus: {!s}".format(self.robot, status))
        return (status)

    ###############################################################################
    ### Function:  waitOnComplete
    ###
    ###   Checks robot status (for Idle/Completed) then returns 'True' or 'False'
    ###   to the caller for use.  If the command has not "COMPLETED", a warning
    ###   is displayed indicating other reason for IDLE to have been reached.
    ###############################################################################
    def waitOnComplete(self,sec=3.0):
        completed = False
        while (completed == False):
            time.sleep(sec)
            completed = self.commandCompleted()
        return

    ###############################################################################
    ### Function:  commandCompleted
    ###
    ###   Checks robot status (for Idle/Completed) then returns 'True' or 'False'
    ###   to the caller for use.  If the command has not "COMPLETED", a warning
    ###   is displayed indicating other reason for IDLE to have been reached.
    ###############################################################################
    def commandCompleted (self):
        completed = False
        curState  = self.getState()
        if curState == "Idle" :
            completed = True
            curStatus = self.getStatus()
            if curStatus != "COMPLETE" :
                self.msgWarn("current planStatus=" + curStatus)
        return completed

    ###############################################################################
    ###  doDriveVelocity - recursive routine to drive robot a given time
    ###############################################################################
    def doDriveVelocity(self,
                        translateIn,
                        sidestepIn,
                        rotateIn,
                        durationIn,
                        nudgeIn,
                        printDots=False,
                        printTimes=False):

        interval = 0.05
        self.postCommand (
                              '/robot/drive/velocity',
                              {"translate":translateIn,
                               "sidestep":sidestepIn,
                               "rotate":rotateIn,
                               "duration":durationIn,
                               "nudge":nudgeIn})

        time.sleep(interval)
        remaining = durationIn-interval
        if durationIn > interval:
            if printDots==True or printDots=='true' or printDots=='True':
                self.msgDebug ('.'),
                sys.stdout.flush()
            elif printTimes==True or printTimes=='true' or printTimes=='True':
                self.msgDebug (time.ctime())
                self.msgDebug ('remaining=' ,remaining , ' interval = ',  interval)
                sys.stdout.flush()
            return self.doDriveVelocity(
                                   translateIn,
                                   sidestepIn,
                                   rotateIn,
                                   remaining,
                                   nudgeIn,
                                   printDots,
                                   printTimes)
        else:
            if printDots==True or printDots=='true' or printDots=='True':
                self.msgDebug ('.'),
                sys.stdout.flush()
            elif printTimes==True or printTimes=='true' or printTimes=='True':
                self.msgDebug (time.ctime(), ('COMPLETED'))
                sys.stdout.flush()
            return 0.0

    def getCoords(self):
        response = json.loads(self.getCommand('/robot/drive/position'))
        X = float(response['x'])
        Y = float(response['y'])
        coordinates = [X,Y]
        return coordinates

    def getNamespaceCoord(self):
        tagList = self.getTagList()
        for key, values in tagList.items():
            N = values['name']
            if ('PatrolNoStop' == N):
                X = float(values['position']['x'])
                Y = float(values['position']['y'])
        coordinates = [X,Y]
        return coordinates

    ###############################################################################
    ### Function:  getDockedStatus
    ###
    ###   Retrieves the data from the robot's updates planStatus field.  This
    ###   command returns more specific information on why robot command has
    ###   stopped (completed, cancelled, etc.).
    ###############################################################################
    def getDockedStatus(self):
        curStatus = self.getCommand('/robot/dock/status')
        json_obj = json.loads(curStatus)
        # if json_obj["status"]=="FAILED":
        #     return "FAILED"
        status = json_obj["state"]
        return status

    ###############################################################################
    ### Function:  dockRobot
    ###
    ###   Retrieves the data from the robot's updates planStatus field.  This
    ###   command returns more specific information on why robot command has
    ###   stopped (completed, cancelled, etc.).
    ###############################################################################
    def dockRobot(self, tagID=None):
        status = False
        if self.getDockedStatus() =="Docked":
            self.msgInfo("Already Docked")
            return
        if tagID is None:
            uri = '/robot/dock/dockTag'
        else:
            uri = '/robot/dock/dockTag?tagId=' + tagID
        self.getCommand(uri)
        self.msgInfo("Going to Dock .")
        self.waitOnComplete()
        if self.getDockedStatus() =="Docked":
            status=True
            self.msgInfo("Successfully Docked")
        else:
            self.getCommand('/robot/dock/dock')
            self.msgInfo("Going to Dock .")
            for x in range(30):
                status = self.getDockedStatus()
                if status =="Docked" or status == "FAILED":
                    break;
                time.sleep(5.0)
                self.msgInfo(".")
            if self.getDockedStatus() =="Docked":
                self.msgInfo("Successfully Docked")
                status=True
            else:
                self.msgWarn("Falied to dock")
        return status


    ###############################################################################
    ### Function:  dockRobot
    ###
    ###   Retrieves the data from the robot's updates planStatus field.  This
    ###   command returns more specific information on why robot command has
    ###   stopped (completed, cancelled, etc.).
    ###############################################################################
    def driveRobotToTag(self,tag="1"):
        response = self.getCommand('/robot/drive/driveToTag/1/'+tag)
        if response:
            return response

    ###############################################################################
    ### Function:  dockHome
    ###
    ###   Dock the robot to its home dock.
    ###############################################################################
    def dockHome(self):
        response = self.getCommand('/robot/drive/goHome?wait=0.0')
        return response
     
    def getCallstatus(self):
        response = json.loads(self.getCommand('/robot/tel/status'))
        if('calls' in response):
            call = response['calls'][0]
            return call['status']
        else:
            return None

    def getSessionState(self):
        response = json.loads(self.getCommand('/robot/tel/getSessionState'))
        state = response['state']
        return state

    def setSessionState(self):
        try:
            response = json.loads(self.getCommand('/robot/tel/setSessionState?state=EMBODIED&user=Welcome'))
            return response
        except:
            self.msgWarn('Set session failed')
            return

    def endSessionState(self):
        try:
            response = json.loads(self.getCommand('/robot/tel/setSessionState?state=IDLE'))
            return response
        except:
            self.msgWarn('End session failed')
            return

    ###############################################################################
    ### Function:  getTagList
    ###
    ###   Get list of all annotated tag lists.
    ###############################################################################
    def getTagList(self):
        try:
            res = self.getCommand('/robot/annotation/tags/1')
            tagList = json.loads(res)
            tagList = tagList["tags"]
            return tagList
        except Exception as e:
            return None

    ###############################################################################
    ### Function:  driveAndRotate
    ###
    ###   Drive to tag, wait to complete, and rotate.
    ###############################################################################
    def driveAndRotate(self,nudgeSetting,tag=2):
        print("Driving to tag :"+str(tag))
        self.driveRobotToTag(tag)
        self.waitOnComplete()
        print("Start Rotation")
        self.postCommand ('/robot/kinematics/look',{"angle":math.pi})
        self.doDriveVelocity(0.00,0.0,1.0,0.5,nudgeSetting,False,False)
        self.waitOnComplete()

    def driveToDestination(self,destination, waitTime=5.0):
         #destination = json.loads(destination)
         self.postCommand ('/robot/drive/destination', destination)
         self.waitOnComplete(waitTime)

    def driveTilt(self,zLift=0.0,cameraTilt=0.0):
         self.postCommand('/robot/drive/payloadPose',{
	                                               "cameraTilt":cameraTilt,
                                                   "zLift":zLift,
                                                   })

    def driveRobot(self,sidestep=0.0,rotate=0.0,translate=0.0):
         self.postCommand('/robot/drive/velocity',{
	                                               "translate":translate,
                                                   "sidestep":sidestep,
                                                   "rotate":rotate,
                                                   "duration":0.5,
                                                   "nudge":False})

    def getZLiftCameraTilt(self):
        robotCamZliftPos = json.loads(self.getCommand('/robot/drive/getZLiftCameraTilt'))
        return (robotCamZliftPos)

    def getCameraPos(self):
        robotCamZliftPos = self.getZLiftCameraTilt()
        return robotCamZliftPos['cameraTilt']['position']

    def getZliftPos(self):
        robotCamZliftPos = self.getZLiftCameraTilt()
        return robotCamZliftPos['zLift']['position']

    def tiltRobotCamerDown(self):
        self.driveTilt(cameraTilt=0.9)

    def tiltRobotCamerUp(self):
        self.driveTilt(cameraTilt=-0.2)

    def zLiftRobotUp(self):
        self.driveTilt(zLift=1)

    def zLiftRobotDown(self):
        self.driveTilt(zLift=0)

    def driveSideStepRight(self):
        self.driveRobot(sidestep=1.0)

    def driveSideStepLeft(self):
         self.driveRobot(sidestep=-1.0)

    def driveRotateNeg(self):
        self.driveRobot(rotate=-1.0)

    def driveRotatePos(self):
        self.driveRobot(rotate=2.0)

    def verifyRobotPosition(self,expectedData):
        expectedData = json.loads(expectedData)
        robotPositionData = self.curRobotPosition()
        print(robotPositionData)
        retVal= (self.compareStringVal(robotPositionData['x'],expectedData['x']) and
        self.compareStringVal(robotPositionData['y'],expectedData['y']) and
        self.compareStringVal(robotPositionData['theta'],expectedData['theta']))
        return retVal

    def compareStringVal(self,actual,expected):
        return round(float(actual))==round(float(expected))

if __name__ == '__main__':
    test = Utils('','','','')
    v = test.getVolume()
    print(v)
