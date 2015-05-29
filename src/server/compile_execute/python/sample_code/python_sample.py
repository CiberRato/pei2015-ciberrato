#
# Authors: Luis Seabra Lopes
# October-November 2013
#


from croblink import *
import sys
from math import *


class MyRob(CRobLink):
    def __init__(self, rob_name, host, rob_id):
        self.counter = 0
        self.prev_ground = 0
        self.start_pos = 0
        self.start_saved = False
        CRobLink.__init__(self, rob_name, rob_id, host)

    def run(self):
        if rob.status != 0:
            print "Connection refused or error"
            quit()

        state = 'stop'
        stopped_state = 'run'

        self.start_saved = False
        self.prev_ground = 99

        while True:
            self.read_sensors()

            if self.measures.groundReady:
                if self.measures.ground != self.prev_ground:
                    self.prev_ground = self.measures.ground

            if self.measures.endLed:
                print self.rob_name + " exiting"
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if not self.start_saved:
                    if self.measures.gpsReady:
                        self.start_pos = (self.measures.x, self.measures.y)  # posicao inicial
                        self.start_saved = True

                if not self.measures.visitingLed and \
                        not self.measures.returningLed and \
                        self.measures.groundReady and self.measures.ground == 0:
                    self.set_visiting_led(True)

                if self.measures.visitingLed:  # quando chegar ao queijo...
                    self.set_visiting_led(False)
                    self.set_returning_led(True)

                if self.measures.returningLed:
                    state = 'return'

                else:
                    l_pow, r_pow = self.determine_action("run")
                    self.drive_motors(l_pow, r_pow)

    def determine_action(self, state):
        collision = False
        beacon_visible = False

        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        center = left = right = back = 0

        if self.measures.irSensorReady[left_id]:
            left = self.measures.irSensor[left_id]
        if self.measures.irSensorReady[right_id]:
            right = self.measures.irSensor[right_id]
        if self.measures.irSensorReady[center_id]:
            center = self.measures.irSensor[center_id]
        if self.measures.irSensorReady[back_id]:
            back = self.measures.irSensor[back_id]

        beacon_ready = self.measures.beacon_ready
        if beacon_ready:
            beacon_visible, beacon_dir = self.measures.beacon

        if self.measures.groundReady:
            ground = self.measures.ground
        if self.measures.collisionReady:
            collision = self.measures.collision

        if center > 4.5 or right > 4.5 or left > 4.5 or collision:
            if self.counter % 400 < 200:
                self.drive_motors(0.06, -0.06)
                self.read_sensors()

            else:
                self.drive_motors(-0.06, 0.06)
                self.read_sensors()

        elif right > 1.5:
            self.drive_motors(0.0, 0.5)
            self.read_sensors()

        elif left > 1.5:
            self.drive_motors(0.05, 0.0)
            self.read_sensors()

        else:
            follow = False
            if state == 'run' and beacon_ready and beacon_visible:
                follow = True
                target_dir = beacon_dir

            if follow and target_dir > 20.0:
                self.drive_motors(0.0, 0.1)
                self.read_sensors()

            elif follow and target_dir < -20.0:
                self.drive_motors(0.1, 0.0)
                self.read_sensors()
            else:
                self.read_sensors()
                self.drive_motors(0.1, 0.1)
                l_pow = 0.1
                r_pow = 0.1

        self.counter += 1
        return l_pow, r_pow


rob_name = "BB"
host = "localhost"
pos = 3

for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-host" and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    if sys.argv[i] == "-pos" and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    if sys.argv[i] == "-rob_name" and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]

rob = MyRob(rob_name, host, pos)
rob.run()
