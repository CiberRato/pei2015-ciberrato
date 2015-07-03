
from croblink import *
import sys
from math import *

FRONT=0
LEFT=1
RIGHT=2
REAR=3

def posX():
    global rob
    return (int)(100.0*rob.measures.x+0.5)

def posY():
    global rob
    return (int)(100.0*rob.measures.y+0.5)

def init2(robName,pos,host):
    global rob,__x0_,__y0_
    rob = CRobLink(robName,pos,host);
    rob.readSensors()
    __x0_ = posX()
    __y0_ = posY()
    while(not rob.measures.start):
        rob.readSensors()

def apply(time):
    global rob
    while(time>0):
        rob.readSensors()
        time = time - 1

def motors(left,right):
    global rob,leftP,rightP
    leftP=left
    rightP=right
    rob.driveMotors(leftP,rightP)

def pickup():
    global rob
    rob.setVisitingLed(True)
    rob.driveMotors(0,0)
    rob.readSensors()
    rob.setVisitingLed(False)
    rob.driveMotors(leftP,rightP)

def returning():
    global rob
    rob.setReturningLed(True)

def finish():
    global rob
    rob.finish()

def obstacleDistance(sensorId):
    global rob
    if (rob.measures.irSensor[sensorId]==0):
        return 1000
    return (int)(100.0 * (1.0/rob.measures.irSensor[sensorId]) + 0.5)
    

def beaconAngle(bId):
    global rob
    (beaconVisible,beaconDir) = rob.measures.beacon[bId-1]  
    return (int)(beaconDir+0.5)

def northAngle():
    global rob
    return (int)(rob.measures.compass+0.5);

def groundType():
    global rob
    return rob.measures.ground+1

def onTarget(tId):
    global rob
    return rob.measures.ground == (tId-1)

def numberOfBeacons():
    global rob
    return rob.parameters.nBeacons;

def ang(x1, y1, x2, y2):
    dx = x2-x1;
    dy = y2-y1;
    if (dx == 0 and dy == 0): 
        return 0
    return (int)(atan2(dy, dx)*180.0/pi + 0.5)

def startAngle():
    global rob, __x0_, __y0_
    theta1 = ang(posX(), posY(), __x0_, __y0_)
    theta2 = rob.measures.compass
    theta = theta1 - theta2
    if (theta > 180): 
        theta -= 360
    elif (theta < -180): 
        theta += 360
    return theta

def startDistance():
    global __x0_, __y0_
    dx = posX() - __x0_
    dy = posY() - __y0_
    #print "startDist px=",posX()," py=",posY()," x0=",__x0_," y0=",__y0_
    dist = (int)(sqrt(dx*dx + dy*dy)+0.5)

    return dist

