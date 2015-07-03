
from CiberAV import *
import sys
from math import *

init2("agent",1,"localhost")
apply(1)
count = 1000
print "beacAng ",beaconAngle(1)
while (beaconAngle(1)>10 or beaconAngle(1)<-10):
   motors(-0.02,0.02)
   apply(1)

while(not onTarget(1)):
   print "GO"
   if (beaconAngle(1)>10):
      motors(0.0,0.1)
   elif (beaconAngle(1)<-10):
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
   if (startAngle()>10):
      motors(0.0,0.1)
   elif (startAngle()<-10):
      motors(0.1,0.0)
   else:
      motors(0.1,0.1)
   apply(1)


finish()
apply(1)

