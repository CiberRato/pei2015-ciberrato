
#
# Authors: Nuno Lau and Luis Seabra Lopes
# October - November 2013
#

import socket
NUM_IR_SENSORS = 4


class CRobLink:
    """
    Class used to simulate the robot.
    """
    def __init__(self, rob_name, rob_id, host):
        """
        Initializes robot and connects to simulator on a given host.
        It registers the robot on the simulator sending a message TCP 
            <Robot Id='robId' Name='robName' />

        Parameters:
            `rob_name`: Robot name that will be used by the simulator
            `rob_id`: The robot identifier (it must be unique for the
                simulation)
            `host`: Hostname of the simulator (might include port, 
                example: 127.0.0.1:4001)
        """
        self.rob_name = rob_name
        self.rob_id = rob_id

        val = host.split(":")
        port_conn = 6000
        if len(val) > 1:
            self.host = val[0]
            port_conn = int(val[1])
        else:
            self.host = host

        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_STREAM)  # UDP
        self.sock.connect((self.host, port_conn))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        msg = '<Robot Id="'+str(rob_id)+'" Name="'+rob_name+'" />\x04'

        self.sock.send(msg)
        data = self.sock.recv(1024)
        # print "received message:", data, " port ", self.port

        parser = sax.make_parser()

        # Tell it what handler to use
        handler = StructureHandler()
        parser.setContentHandler(handler)

        # Parse reply
        d2 = data.split('\x04')[0]
        sax.parseString(d2, handler)
        self.status = handler.status

    def read_sensors(self):
        """
        This functions read all the sensors available given by the 
            simulator, storing them at measures field.

        Measures field (CMeasures object) is composed by:
            compassReady    * True if compass value is available to be 
                                read
            compass         * Compass value (value between 0 and 360) 
            irSensorReady   * True if sensor is available (list of 
                                sensors - NUM_IR_SENSORS)
            irSensor        * Sensor value (the more closer to the 
                                obstacle, the bigger is the value)
            beaconReady     * True if beacon is available to be read
            beacon          * Returns a tuple of (bool, float) where 
                                the bool represents if the Beacon is
                                visible and the float represents the 
                                distance when visible
            time = 0        * Current time of the simulation
            groundReady     * True if ground sensor is available to 
                                be read
            ground          * True if robot detects the ground as a 
                                target area
            collisionReady  * True if collision sensor is available 
                                to be read
            collision       * True if robot as collided
            start           * True if the button start was pressed
            stop            * True if the button end was pressed
            endLed          * True when the end led has been turned
            returningLed    * True when the returning led has been 
                                turned on
            visitingLed     * True when the visiting led has been 
                                turned on
            gpsReady        * True when GPS is available 
            gpsDirReady     * True when GPS direction is available
            x               * Current x-axis position of the robot, 
                                GPS must be enabled
            y               * Current y-axis position of the robot, 
                                GPS must be enabled
            dir             * Current direction of the robot, GPS 
                                must be enabled
            scoreReady      * Simulation score is ready to be read
            score           * Returns the current score of the robot
            arrivalTimeReady    * True when available to be read
            arrivalTime         * Current arrival time of the robot
            returningTimeReady  * True when available to be read
            returningTime       * Current returning time of the robot
            collisionsReady     * True when available to be read
            collisions          * Returns the number of collisions
            hearMessage         * Used to communicate between robots
        """
        data = self.sock.recv(4096)
        d2 = data.split('\x04')[0]

        # print "Received : \"" + d2 +'"'
        parser = sax.make_parser()
        # Tell it what handler to use
        handler = StructureHandler()
        parser.setContentHandler(handler)

        sax.parseString(d2, handler)
        self.status = handler.status
        self.measures = handler.measures

    def sync_robot(self):
        """
        This function is used to signal the simulator that the robot 
        has done everything that he wanted in that cycle and he is 
        ready to process the next cycle.

        This function must be used when simulator is running in
        synchronous mode, otherwise it will run every cycle till the
        real cycle time (takes longer).
        """
        msg = '<Actions> <Sync/> </Actions>\x04'
        self.sock.send(msg)

    def drive_motors(self, lpow, rpow):
        """
        This function signals the simulator the speed for each wheel of
        the robot.

        Parameters:
            `lpow` - Speed for the left motor (value between 0 and 1)
            `rpow` - Speed for the right motor (value between 0 and 1)
        """
        msg = '<Actions LeftMotor="' + \
            str(lpow)+'" RightMotor="'+str(rpow)+'"/>\x04'
        self.sock.send(msg)

    def set_returning_led(self, val):
        """
        This function turns on or off the returning led to signal that 
        the robot is returning to the initial position.

        Parameters:
            `val` - True to set the led on, False otherwise
        """
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" ' + \
            'ReturningLed="' + ("On" if val else "Off") + '"/>\x04'
        self.sock.send(msg)

    def set_visiting_led(self, val):
        """
        This function turns on or off the visiting led to signal that 
        the robot reached the beacon.

        Parameters:
            `val` - True to set the led on, False otherwise
        """
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" ' + \
            'VisitingLed="' + ("On" if val else "Off") + '"/>\x04'
        self.sock.send(msg)

    def finish(self):
        """
        This function signals the simulator that the robot has ended
        the simulation and doesn't want to take more actions.
        """
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" ' + \
            'EndLed="On"/>\x04'
        self.sock.send(msg)


class CMeasures:
    """
    Structure where the values read from the simulator are stored.
    """
    def __init__(self):
        self.compassReady = False
        self.compass = 0.0
        self.irSensorReady = [False for i in range(NUM_IR_SENSORS)]
        self.irSensor = [0.0 for i in range(NUM_IR_SENSORS)]
        self.beaconReady = False 
        self.beacon = (False, 0.0)
        self.time = 0

        self.groundReady = False
        self.ground = False
        self.collisionReady = False
        self.collision = False
        self.start = False
        self.stop = False
        self.endLed = False
        self.returningLed = False
        self.visitingLed = False
        self.x = 0.0
        self.y = 0.0
        self.dir = 0.0

        self.scoreReady = False
        self.score = 100000
        self.arrivalTimeReady = False
        self.arrivalTime = 10000
        self.returningTimeReady = False
        self.returningTime = 10000
        self.collisionsReady = False
        self.collisions = 0
        self.gpsReady = False
        self.gpsDirReady = False

        self.hearMessage = ''

from xml import sax


class StructureHandler(sax.ContentHandler):
    """
    Class used to process the messages sent by the simulator (parser).
    """
    def __init__(self):
        self.status = 0
        self.measures = CMeasures()

    def startElement(self, name, attrs):
        # print attrs
        if name == "Reply":
            if "Status" not in attrs.keys():
                self.status = -1
                return

            if attrs["Status"] == "Ok":
                self.status = 0
                return
            self.status = -1
        elif name == "Measures":
            self.measures.time = int(attrs["Time"])
        elif name == "Sensors":
            self.measures.compassReady = ("Compass" in attrs.keys())
            if self.measures.compassReady:
                self.measures.compass = float_of_string(attrs["Compass"])

            self.measures.collisionReady = ("Collision" in attrs.keys())
            if self.measures.collisionReady:
                self.measures.collision = (attrs["Collision"] == "Yes")

            self.measures.groundReady = ("Ground" in attrs.keys())
            if self.measures.groundReady:
                self.measures.ground = int(attrs["Ground"])

        elif name == "IRSensor":
            id = int(attrs["Id"])
            # print "IRSensor id ", id
            if id < NUM_IR_SENSORS:
                self.measures.irSensorReady[id] = True
                # print "IRSensor val ", attrs["Value"]
                self.measures.irSensor[id] = float_of_string(attrs["Value"])
            else:
                self.status = -1
        elif name == "BeaconSensor":
            id = attrs["Id"]
            # if id<self.measures.beaconReady.len():
            if 1:
                self.measures.beaconReady = True
                # print attrs["Value"]
                if attrs["Value"] == "NotVisible":
                    # self.measures.beaconReady[id]=(False,0.0)
                    self.measures.beacon = (False, 0.0)
                else:
                    # self.measures.beaconReady[id]=(True,attrs["Value"])
                    self.measures.beacon = (
                        True, float_of_string(attrs["Value"]))
            else:
                self.status = -1
        elif name == "GPS":
            if "X" in attrs.keys():
                self.measures.gpsReady = True
                # print attrs["X"]
                self.measures.x = float_of_string(attrs["X"])
                self.measures.y = float_of_string(attrs["Y"])
                if "Dir" in attrs.keys():
                    self.measures.gpsDirReady = True
                    self.measures.dir = float_of_string(attrs["Dir"])
                else:
                    self.measures.gpsDirReady = False
            else:
                self.measures.gpsReady = False
        elif name == "Leds":
            self.measures.endLed = (attrs["EndLed"] == "On")
            self.measures.returningLed = (attrs["ReturningLed"] == "On")
            self.measures.visitingLed = (attrs["VisitingLed"] == "On")
        elif name == "Buttons":
            self.measures.start = (attrs["Start"] == "On")
            self.measures.stop = (attrs["Stop"] == "On")
        elif name == "Score":
            self.measures.scoreReady = ("Score" in attrs.keys())
            if self.measures.scoreReady:
                self.measures.score = int(attrs["Score"])
            self.measures.arrivalTimeReady = ("ArrivalTime" in attrs.keys())
            if self.measures.arrivalTimeReady:
                self.measures.arrivalTime = int(attrs["ArrivalTime"])
            self.measures.returningTimeReady = (
                "ReturningTime" in attrs.keys())
            if self.measures.returningTimeReady:
                self.measures.returningTime = int(attrs["ReturningTime"])
            self.measures.collisionsReady = ("Collisions" in attrs.keys())
            if self.measures.collisionsReady:
                self.measures.collisions = int(attrs["Collisions"])
        elif name == "Message":
            self.hearFrom = int(attrs["From"])

    # def endElement(self, name):
        # print 'End of element:', name


def float_of_string(str):
    """
    Function used to convert a string to a float
    """
    s = ""
    for c in str:
        if c == ",":
            s += "."
        else:
            s += c
    # print "--" + s + "--"
    return float(s)
