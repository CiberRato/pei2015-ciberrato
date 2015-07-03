
# Robotica em ambiente simulado
# Academia de Verao 2015
# Contactos: artur@ua.pt, nunolau@ua.pt
#
# Departamento de Electronica, Telecomunicacoes e Informatica
# Universidade de Aveiro

from CiberAV import *
import sys
from math import *

rob_name = "agent"
host = "localhost"
pos = 1

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-host" and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    if sys.argv[i] == "-pos" and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    if sys.argv[i] == "-robname" and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]

if not init2(rob_name, pos, host):                     # connect to simulator
    sys.exit(1)

print "ALIGN WITH BEACON"
while (beaconAngle(1)>10 or beaconAngle(1)<-10):   # while angle error to beacon higher than 10
    motors(-0.02,0.02)                             #   rotate
    apply(1)                                       #   after each motors, apply is needed!
    print "beaconAng=",beaconAngle(1)

print "GOTO BEACON"
while(not onTarget(1)):                           # while not inside target region 1
    if (beaconAngle(1)<-10):                      # if not aligned with target
        motors(0.1,0.0)                           #    align
    elif (beaconAngle(1)>10):                     # if not aligned with target
        motors(0.0,0.1)                           #    align
    else:
        motors(0.1,0.1)                           # if aligned go straight
    apply(1)

print "STOP AND PICKUP"
motors(0.0,0.0);                                  # stop
pickup()                                          # pickup
apply(1)

print "RETURNING"
returning()                                       # initiate return to start pos
apply(1)

print "FINISH"
finish()                                         # The End!
