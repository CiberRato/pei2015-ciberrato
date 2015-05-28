from math import *

from croblink import *


class MyRob(CRobLink):
    def run(self):
        if rob.status != 0:
            print "Connection refused or error"
            quit()

        state = 'stop'
        stopped_state = 'run'

        self.start_saved = False
        self.prev_ground = 99

        self.counter = 0

        while True:
            self.readSensors()

            if self.measures.ground_ready:
                if self.measures.ground != self.prev_ground:
                    print state, "ground=", self.measures.ground
                    self.prev_ground = self.measures.ground

            if self.measures.endLed:
                print self.robName + " exiting"
                quit()

            if (state == 'stop' and self.measures.start):
                state = stopped_state

            if (state != 'stop' and self.measures.stop):
                stopped_state = state
                state = 'stop'

            if (state == 'run'):
                if not self.start_saved:
                    if self.measures.gpsReady:
                        self.start_pos = (self.measures.x, self.measures.y)
                        self.start_saved = True
                if not self.measures.visitingLed and \
                        not self.measures.returningLed and \
                        self.measures.ground_ready and self.measures.ground == 0:
                    self.setVisitingLed(True)
                    print self.robName + " visited target area"
                if self.measures.visitingLed:
                    self.setVisitingLed(False)
                    self.setReturningLed(True)
                if self.measures.returningLed:
                    state = 'return'
                else:
                    (lPow, rPow) = self.determine_action("run")
                    self.driveMotors(lPow, rPow)

            if (state == 'return'):
                if self.measures.ground_ready and self.measures.ground == 1:
                    self.finish()
                    print self.robName + " found home area"
                elif self.measures.gpsReady and \
                                dist((self.measures.x, self.measures.y), self.start_pos) < 0.5:
                    self.finish()
                    print self.robName + " really close to start position"
                else:
                    (lPow, rPow) = self.determine_action("return")
                    self.driveMotors(lPow, rPow)
            self.syncRobot()

    def determine_action(self, state):

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

        beacon_ready = self.measures.beaconReady
        if beacon_ready:
            (beaconVisible, beaconDir) = self.measures.beacon

        if self.measures.ground_ready:
            ground = self.measures.ground
        if self.measures.collisionReady:
            collision = self.measures.collision

        if center > 4.5 or right > 4.5 or left > 4.5 or collision:
            if self.counter % 400 < 200:
                lPow = 0.06
                rPow = -0.06
            else:
                lPow = -0.06
                rPow = 0.06
        elif right > 1.5:
            lPow = 0.0
            rPow = 0.05
        elif left > 1.5:
            lPow = 0.05
            rPow = 0.0
        else:
            follow = False
            if state == 'run' and beacon_ready and beaconVisible:
                print "run to beacon"
                follow = True
                target_dir = beaconDir
            elif state == "return" and self.measures.gpsReady \
                    and self.measures.compassReady:
                print "return to home"
                follow = True
                dx = self.start_pos[0] - self.measures.x
                dy = self.start_pos[1] - self.measures.y
                abs_target_dir = atan2(dy, dx) * 180 / 3.141592
                target_dir = abs_target_dir - self.measures.compass
                if target_dir > 180:
                    target_dir -= 360
                elif target_dir < -180:
                    target_dir += 360

            if follow and target_dir > 20.0:
                lPow = 0.0
                rPow = 0.1
            elif follow and target_dir < -20.0:
                lPow = 0.1
                rPow = 0.0
            else:
                lPow = 0.1
                rPow = 0.1

        self.counter += 1
        return lPow, rPow


def dist(p, q):
    (px, py) = p
    (qx, qy) = q
    return sqrt((px - qx) ** 2 + (py - qy) ** 2)


robname = "BB"
host = "localhost"
pos = 3
for i in range(0, len(sys.argv)):
    if sys.argv[i] == "-host" and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    if sys.argv[i] == "-pos" and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    if sys.argv[i] == "-robname" and i != len(sys.argv) - 1:
        robname = sys.argv[i + 1]

rob = MyRob(robname, pos, host)
rob.run()

