from croblink import CRobotLink
import sys
from math import *
from socket import *
import random


class MyRobot(CRobotLink):
    def __init__(self, robot_name, host, robot_id):
        self.robot_name = robot_name
        self.counter = 0
        CRobotLink.__init__(self, robot_name, robot_id, host)
        print "Robot %s Initialized in position %d" % (robot_name, robot_id)

    def run(self):
        """
        Main Run loop
        """
        if self.status != 0:
            print "Connection to simulator was refused or returned an error %d" % self.status
            sys.exit(-1)

        print "Robot Run loop"
        state = 'stop'

        while True:
            self.counter += 1
            print "Counter=%d" % self.counter

            # Read Sensors
            self.request_sensors(['Beacon', 'Ground', 'Compass', 'IRSensor'])
            self.read_sensors()  # Update sensor measures

            # Start button is pressed?
            if self.measures.start and state != "run":
                print "Running"
                state = "run"

            # Stop button was pressed?
            if self.measures.stop and state != "stop":
                print "Stopping"
                state = 'stop'

            if state == 'run':
                if self.measures.ground == 1:
                    print "Robot %s reached the target" % (self.robot_name)
                    left_power = right_power = 0
                    self.set_visiting_led('On')
                    self.finish()

                else:
                    left_power, right_power = self.determine_action("run")

                print "Power: %f %f" % (left_power, right_power)

                self.drive_motors(left_power, right_power)

            self.sync_robot()  # Sync with simulator

    def determine_action(self, state):
        """
        Main function to determine the action to take
        """

        left = self.measures.ir_sensor_left
        right = self.measures.ir_sensor_right
        center = self.measures.ir_sensor_center

        beacon = self.measures.beacon
        collision = self.measures.collision
        compass = self.measures.compass

        try:
            print "Sensors: Left=%s Center=%s Right=%s Back=%s Collision=%s Beacon=%s" %(str(left), str(center), str(right), str(beacon), str(collision), str(beacon))
        except:
            pass

        left_power = 0  # Left engine power
        right_power = 0  # Right engine power

        #
        # Add your code here and replace this dummy code!
        #

        if collision == 1 or center > 2:
            print "On Collision Course!"
            left_power = -1
            right_power = 1
        else:
            print "Warp Speed!"
            left_power = 1
            right_power = 1

        return left_power*0.15, right_power*0.15

#
# Lets parse the command line
# Create the Robot and connect to the Simulator
#
if __name__ == "__main__":
    robot_name = "BB"
    hostname = "localhost:6000"
    position = 3

    for i in range(0, len(sys.argv)):
        if sys.argv[i] == "-host" and i != len(sys.argv) - 1:
            hostname = sys.argv[i + 1]
        if sys.argv[i] == "-position" and i != len(sys.argv) - 1:
            position = int(sys.argv[i + 1])
        if sys.argv[i] == "-robotname" and i != len(sys.argv) - 1:
            robot_name = sys.argv[i + 1]

    # We are ready to GO!
    robot = MyRobot(robot_name, hostname, position)
    robot.run()
