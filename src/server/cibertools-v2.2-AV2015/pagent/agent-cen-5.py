
from CiberAV import *
import sys
from math import *

init2("agent",1,"localhost")

print "numberofbeacs ", numberOfBeacons()

for beaconId in range(1,numberOfBeacons()+1):
   apply(1)
   print "beacAng ",beaconAngle(beaconId)
   while (beaconAngle(beaconId)>10 or beaconAngle(beaconId)<-10):
      print "beaconAng=",beaconAngle(beaconId)
      motors(-0.02,0.02)
      apply(1)

   while(not onTarget(beaconId)):
      print "GO oDist",obstacleDistance(FRONT)
      if (obstacleDistance(FRONT)<30):
         motors(-0.05,0.05)
      elif (obstacleDistance(LEFT)<50):
         motors(0.05,0.00)
      elif (obstacleDistance(RIGHT)<50):
         motors(0.00,0.05)
      elif (beaconAngle(beaconId)<-10):
         motors(0.1,0.0)
      elif (beaconAngle(beaconId)>10):
         motors(0.0,0.1)
      elif (beaconAngle(beaconId)<-10):
         motors(0.1,0.0)
      else:
         motors(0.1,0.1)
      apply(1)

   motors(0.0,0.0);
   print "STOP"
   apply(10)
   pickup()
   apply(1)

returning()
apply(1)


while (startAngle()>10 or startAngle()<-10):
   motors(0.02,-0.02)
   apply(1)

while(startDistance()>50):
   print "GO dist ", startDistance()," ang ",startAngle()
   if (obstacleDistance(FRONT)<30):
      motors(-0.05,0.05)
   elif (obstacleDistance(LEFT)<50):
      motors(0.05,0.00)
   elif (obstacleDistance(RIGHT)<50):
      motors(0.00,0.05)
   elif (startAngle()>10):
      motors(0.0,0.1)
   elif (startAngle()<-10):
      motors(0.1,0.0)
   else:
      motors(0.1,0.1)
   apply(1)


finish()
apply(1)

