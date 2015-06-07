# encoding=utf-8
#
# Authors: Nuno Lau and Luis Seabra Lopes
# October - November 2013
#
# Simplified by João Paulo Barraca
# May 2015
#

import socket
NUM_IR_SENSORS = 4

class CRobotLink:
    """
    Class used to simulate the robot.
    """
    def __init__(self, name, identifier, host):
        """
        Initializes robot and connects to simulator on a given host.
        It registers the robot on the simulator sending a message TCP
            <Robot Id='robId' Name='robName' />

        Parameters:
            `name`: Robot name that will be used by the simulator
            `identifier`: The robot identifier (it must be unique for the
                simulation)
            `host`: Hostname of the simulator (might include port,
                example: 127.0.0.1:4001)
        """
        self.name = name
        self.identifier = identifier
        self.pending_sensors = ""
        self.pending_motors = ""

        val = host.split(":")
        port_conn = 6000

        if len(val) > 1:
            self.host = val[0]
            port_conn = int(val[1])
        else:
            self.host = host

        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_STREAM)  # UDP
        self.sock.settimeout(30)
        self.sock.connect((self.host, port_conn))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        msg = '<Robot Id="%s" Name="%s" />\x04' % (str(identifier), name)

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

    def request_sensors(self, sensors):
        if len(sensors) == 0:
            return

        s = "<SensorRequests "
        for sensor in sensors:
            if sensor == "Beacon":
                s += " Beacon0=\"Yes\""
            elif sensor == "IRSensor":
                s += " IRSensor0=\"Yes\"  IRSensor1=\"Yes\" IRSensor2=\"Yes\" IRSensor3=\"Yes\""
            else:
                s += " %s=\"Yes\"" % sensor
        s += "/>"
        self.pending_sensors = s

    def read_sensors(self):
        """
        This functions read all the sensors available given by the
            simulator, storing them at measures field.

        Measures field (CMeasures object) is composed by:
            compass         * Compass value (value between 0 and 360)
            ir_sensor        * Sensor value (the more closer to the
                                obstacle, the bigger is the value)
            beacon          * Returns the distance to the Beacon
                                if visible
            time = 0        * Current time of the simulation
            ground          * True if robot detects the ground as a
                                target area
            collision       * True if robot as collided
            start           * True if the button start was pressed
            stop            * True if the button end was pressed
            end_led          * True when the end led has been turned
            returning_led    * True when the returning led has been
                                turned on
            visiting_led     * True when the visiting led has been
                                turned on
            gps_x           * Current x-axis position of the robot,
                                GPS must be enabled
            gps_y           * Current y-axis position of the robot,
                                GPS must be enabled
            direction       * Current direction of the robot, GPS
                                must be enabled
            score           * Returns the current score of the robot
            arrival_time    * Current arrival time of the robot
            returning_time  * Current returning time of the robot
            collisions      * Returns the number of collisions
            hear_message    * Used to communicate between robots

            All fields can have a value or be equal to None if the
            item is not available.
        """
        data = ""
        try:
            data = self.sock.recv(4096).strip()
            #print "Received : \n%s" % data

            d2 = data.split('\x04')[0]

            parser = sax.make_parser()
            # Tell it what handler to use
            handler = StructureHandler()
            parser.setContentHandler(handler)

            sax.parseString(d2, handler)
            self.status = handler.status
            self.measures = handler.measures
        except:
            print "ERROR Parsing server response: %s" % data
            pass

    def sync_robot(self):
        """
        This function is used to signal the simulator that the robot
        has done everything that he wanted in that cycle and he is
        ready to process the next cycle.

        This function must be used when simulator is running in
        synchronous mode, otherwise it will run every cycle till the
        real cycle time (takes longer).
        """

        msg = "<Actions %s>%s</Actions>\x04" % (self.pending_motors, self.pending_sensors)
        #print "Sending: \n %s" % msg

        self.sock.send(msg)
        self.pending_motors = ""
        self.pending_sensors = ""
        msg = '<Actions> <Sync/> </Actions>\x04'

        #print "Sending: \n %s" % msg
        self.sock.send(msg)

    def drive_motors(self, lpow, rpow):
        """
        This function signals the simulator the speed for each wheel of
        the robot.

        Parameters:
            `lpow` - Speed for the left motor (value between 0 and 1)
            `rpow` - Speed for the right motor (value between 0 and 1)
        """
        self.pending_motors = 'LeftMotor="' + \
            str(lpow)+'" RightMotor="'+str(rpow)+'"'

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
        self.compass = None
        self.ir_sensor = [None for i in range(NUM_IR_SENSORS)]
        self.ir_sensor_center = None
        self.ir_sensor_left = None
        self.ir_sensor_right = None
        self.ir_sensor_back = None

        self.beacon = None
        self.time = None

        self.ground = None
        self.collision = None
        self.start = None
        self.stop = None
        self.end_led = None
        self.returning_led = None
        self.visiting_led = None
        self.x = None
        self.y = None
        self.dir = None

        self.score = None
        self.arrival_time = None
        self.returning_time = None
        self.collisions = None

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
            if "Compass" in attrs:
                self.measures.compass = float_of_string(attrs["Compass"])

            if "Collision" in attrs:
                self.measures.collision = (attrs["Collision"] == "Yes")

            if "Ground" in attrs:
                self.measures.ground = int(attrs["Ground"])

        elif name == "IRSensor":
            id = int(attrs["Id"])
            # print "IRSensor id ", id
            if id < NUM_IR_SENSORS:
                if id == 0:
                    self.measures.ir_sensor_center = float_of_string(attrs["Value"])
                elif id == 1:
                    self.measures.ir_sensor_left = float_of_string(attrs["Value"])
                elif id == 2:
                    self.measures.ir_sensor_right = float_of_string(attrs["Value"])
                elif id == 3:
                    self.measures.ir_sensor_back = float_of_string(attrs["Value"])

                self.measures.ir_sensor[id] = float_of_string(attrs["Value"])
            else:
                self.status = -1

        elif name == "BeaconSensor":
            id = attrs["Id"]
            # if id<self.measures.beaconReady.len():
            # print attrs["Value"]
            if attrs["Value"] == "NotVisible":
                # self.measures.beaconReady[id]=(False,0.0)
                self.measures.beacon = False
            else:
                # self.measures.beaconReady[id]=(True,attrs["Value"])
                self.measures.beacon = float_of_string(attrs["Value"])

        elif name == "GPS":
            if "X" in attrs.keys():
                # print attrs["X"]
                self.measures.gps_x = float_of_string(attrs["X"])
                self.measures.gps_y = float_of_string(attrs["Y"])
                if "Dir" in attrs.keys():
                    self.measures.direction = float_of_string(attrs["Dir"])

        elif name == "Leds":
            self.measures.end_led = (attrs["EndLed"] == "On")
            self.measures.returning_led = (attrs["ReturningLed"] == "On")
            self.measures.visiting_led = (attrs["VisitingLed"] == "On")
        elif name == "Buttons":
            self.measures.start = (attrs["Start"] == "On")
            self.measures.stop = (attrs["Stop"] == "On")
        elif name == "Score":
            if "Score" in attrs.keys():
                self.measures.score = int(attrs["Score"])

            if "ArrivalTime" in attrs.keys():
                self.measures.arrival_time = int(attrs["ArrivalTime"])

            if "ReturningTime" in attrs.keys():
                self.measures.returning_time = int(attrs["ReturningTime"])

            if "Collisions" in attrs.keys():
                self.measures.collisions = int(attrs["Collisions"])
        elif name == "Message":
            self.hearFrom = int(attrs["From"])

    # def endElement(self, name):
        # print 'End of element:', name


def float_of_string(str):
    """
    Function used to convert a string to a float
    """
    return float(str.replace(',', '.'))
