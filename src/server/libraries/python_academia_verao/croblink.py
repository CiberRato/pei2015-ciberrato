
#
# Authors: Nuno Lau and Luis Seabra Lopes
# October-November 2013
#

import socket

NUM_IR_SENSORS = 4

class CRobLink:

    def __init__ (self, robName, robId, host):
        self.robName = robName
        self.robId = robId
        self.measures   = CMeasures()
        self.parameters = CParameters()

        val = host.split(":")
        port_conn = 6000
        if len(val) > 1:
            self.host = val[0]
            port_conn = int(val[1])
        else:
            self.host = host

        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_STREAM) # UDP
        self.sock.connect((self.host, port_conn))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        msg = '<Robot Id="'+str(robId)+'" Name="'+robName+'" />\x04'
        
        self.sock.send(msg)  # TODO consider host arg
        data = self.sock.recv(1024)
        #print "received message:", data

        parser = sax.make_parser()
        
        # Tell it what handler to use
        handler = StructureHandler()
        parser.setContentHandler( handler )
        
        # Parse reply 
        d2 = data.split('\x04')[0]
        sax.parseString( d2, handler )
        self.status = handler.status
        self.parameters = handler.parameters

    def readSensors(self):
        data = self.sock.recv(4096)
        d2 = data.split('\x04')[0]

        # print "RECV : \"" + d2 +'"'
        parser = sax.make_parser()
        # Tell it what handler to use
        handler = StructureHandler()
        parser.setContentHandler( handler )

        sax.parseString( d2, handler )
        self.status = handler.status
        self.measures   = handler.measures
    
    def syncRobot(self):
        msg = '<Actions> <Sync/> </Actions>\x04'
        self.sock.send(msg)

    def driveMotors(self, lPow, rPow):
        msg = '<Actions LeftMotor="'+str(lPow)+'" RightMotor="'+str(rPow)+'"/>\x04'
        # print "MSG", msg
        self.sock.send(msg)

    def setReturningLed(self,val):
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" ReturningLed="'+ ("On" if val else "Off") +'"/>\x04'
        self.sock.send(msg)

    def setVisitingLed(self,val):
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" VisitingLed="'+ ("On" if val else "Off") +'"/>\x04'
        self.sock.send(msg)

    def finish(self):
        msg = '<Actions LeftMotor="0.0" RightMotor="0.0" EndLed="On"/>\x04'
        self.sock.send(msg)


class CMeasures:

    def __init__ (self):
        self.compassReady=False
        self.compass=0.0; 
        self.irSensorReady=[False for i in range(NUM_IR_SENSORS)]
        self.irSensor=[0.0 for i in range(NUM_IR_SENSORS)]
        self.beaconReady = [False for i in range(5)]  # TODO more than 5 beacons
        self.beacon = [(False, 0.0) for i in range(5)]
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

        self.hearMessage=''

class CParameters:

    def __init__ (self):
        self.nBeacons=1


from xml import sax

class StructureHandler(sax.ContentHandler):

    def __init__ (self):
        self.status = 0
        self.measures   = CMeasures()
        self.parameters = CParameters()

    def startElement(self, name, attrs):
        # print attrs
        if name == "Reply":
            if "Status" not in attrs.keys():
                self.status = -1
                return
                
            if attrs["Status"]=="Ok":
                self.status = 0
            else:
                self.status = -1

        elif name=="Parameters":
            self.parameters.nBeacons = int(attrs["NBeacons"])
            #print "NBEACONS=",self.parameters.nBeacons

        elif name=="Measures":
            self.measures.time = int(attrs["Time"])
        elif name=="Sensors":
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
            #print "IRSensor id ", id
            if id < NUM_IR_SENSORS: 
                self.measures.irSensorReady[id] = True
                #print "IRSensor val ", attrs["Value"]
                self.measures.irSensor[id] = float_of_string(attrs["Value"])
            else: 
                self.status = -1
        elif name == "BeaconSensor":
            id = int(attrs["Id"])
            #if id<self.measures.beaconReady.len():
            if 1:
                self.measures.beaconReady[id]=True
                #print attrs["Value"]
                if attrs["Value"] == "NotVisible":
                    #self.measures.beaconReady[id]=(False,0.0)
                    self.measures.beacon[id]=(False,0.0)
                else:
                    #self.measures.beaconReady[id]=(True,attrs["Value"])
                    self.measures.beacon[id]=(True,float_of_string(attrs["Value"]))
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
            self.measures.returningTimeReady = ("ReturningTime" in attrs.keys())
            if self.measures.returningTimeReady:
                 self.measures.returningTime = int(attrs["ReturningTime"])
            self.measures.collisionsReady = ("Collisions" in attrs.keys())
            if self.measures.collisionsReady:
                 self.measures.collisions = int(attrs["Collisions"])
        elif name == "Message":
            self.hearFrom = int(attrs["From"])


#    def endElement(self, name):
        #print 'End of element:', name


def float_of_string(str):
    s = ""
    for c in str:
        if c==",":
            s += "."
        else:
            s += c
    # print "--" + s + "--"
    return float(s)
