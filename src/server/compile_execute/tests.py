# encoding=UTF-8
#import pytest
import os.path
import subprocess
import socket
import time
import sys
from xml.dom import minidom

class Validator:
	def __init__(self):
		self.simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
		self.simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000

	def validate(self):
		#if not os.path.exists('prepare.sh'):
		if not os.path.exists('execute.sh'):
			error("execute.sh was not found. Use it, otherwise to indicate the proper way to run your files.")
		# I don't want stdout log from compilation, just stderr.
		# Bash -e -o pipefail will check for return codes in every single line.
		if os.path.exists('prepare.sh'):
			comp = subprocess.Popen("bash -e -o pipefail prepare.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, stdout=subprocess.PIPE)
			(stdout, stderr) = comp.communicate()
			if comp.returncode != 0:
				error(stderr)

		## At this point we got every file compiled, or at least, it should be.
		# Lets make sure that everything is ready!

		# Should allow to change names
		self.validateRobotName("myrobot")
		self.validateRobotName("thisisaaname")
		self.validatePosition("1")
		self.validatePosition("5")

		print "Success"
		sys.exit(0)

	def validateRobotName(self, name):
		agent = subprocess.Popen("bash -e -o pipefail execute.sh 127.0.0.1 1 "+name, 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		data, (host, port) = self.simulator_dummy.recvfrom(1024) # infos de quem envia

		parametersXML = minidom.parseString(data.replace("\x00", ""))
		robotParam = parametersXML.getElementsByTagName('Robot')
		nameRobot = robotParam[0].attributes['Name'].value

		if nameRobot != name:
			error("execute.sh doesn't allow to change agent name.\n"
				"Please check that the third parameter on execute.sh should be able to change agent name.")

	def validatePosition(self, pos):
		agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 "+pos+" robot", 
							shell=True, stdout=subprocess.PIPE)

		data, (host, port) = self.simulator_dummy.recvfrom(1024) # infos de quem envia

		parametersXML = minidom.parseString(data.replace("\x00", ""))
		robotParam = parametersXML.getElementsByTagName('Robot')
		ID = robotParam[0].attributes['Id'].value

		if ID != pos:
			error("execute.sh doesn't allow to change robot position.\n"
				"Please check that the second parameter on execute.sh should be able to change agent position.")


def error(message):
	sys.stderr.write(message)
	sys.exit(1)

if __name__ == "__main__":
	Validator().validate()

def test_host():
	simulator_dummy = create_simulator()

	agentPath = "cibertools-v2.2/robsample/robsample_python.py"
	host = "127.0.0.1"
	simulator_dummy.bind((host, 6000)) # ouvir na porta 6000	
	agent = subprocess.Popen("./prepare.sh; ./execute.sh "+host+" 1 robot", 
					shell=True, stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia
	print data #só para verificar o que foi recebido

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	assert parametersXML.getElementsByTagName('Robot') != None

	robotParam = parametersXML.getElementsByTagName('Robot')

	assert robotParam[0].attributes['Id'] != None
	assert int(robotParam[0].attributes['Id'].value) >= 0 

	assert robotParam[0].attributes['Name'] != None

	simulator_dummy.close()



	simulator_dummy = create_simulator()

	host = "127.0.0.2"
	simulator_dummy.bind((host, 6000)) # ouvir na porta 6000	
	agent = subprocess.Popen("./prepare.sh; ./execute.sh "+host+" 1 robot", 
					shell=True, stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	assert parametersXML.getElementsByTagName('Robot') != None

	robotParam = parametersXML.getElementsByTagName('Robot')

	assert robotParam[0].attributes['Id'] != None
	assert int(robotParam[0].attributes['Id'].value) >= 0 

	assert robotParam[0].attributes['Name'] != None


def test_Parameters():
	simulator_dummy = create_simulator()

	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000
	agentPath = "cibertools-v2.2/robsample/robsample_python.py"

	agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 1 robot", 
					shell=True, stdout=subprocess.PIPE)

	data, (host_robot, port_robot) = simulator_dummy.recvfrom(1024) # infos de quem envia
	print data

	parameters = '<Reply Status="Ok">\
		<Parameters SimTime="1800" CycleTime="50"\
		CompassNoise="2" BeaconNoise="2" ObstacleNoise="0.1"\
		MotorsNoise="1.5" KeyTime="1350"\
		GPS="On" GPSLinNoise="0.5" GPSDirNoise="5"\
		ScoreSensor="Off" ShowActions="True" NBeacons="1"\
		NRequestsPerCycle="4"\
		ObstacleRequestable="On" BeaconRequestable="On"\
		GroundRequestable="On" CompassRequestable="On"\
		CollisionRequestable="Off"\
		ObstacleLatency="0" BeaconLatency="4"\
		GroundLatency="0" CompassLatency="4"\
		CollisionLatency="0"\
		BeaconAperture="3.141593"\
		ReturnTimePenalty="25" ArrivalTimePenalty="100"\
		CollisionWallPenalty="2" CollisionRobotPenalty="2"\
		TargetReward="100" HomeReward="100" /></Reply>\n'

	
	simulator_dummy.sendto(parameters ,(host_robot, port_robot))


	


 	#data, (host, port) = simulator_dummy.recvfrom(1024)
# #------------------------1º teste-----------------------------------

	readSensorsParam = '<Measures Time="345">\
		<Sensors Collision="No">\
		<GPS X="845.5" Y="403.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
		<Buttons Start="On" Stop="Off"/>\
		</Measures>\n'
	
	simulator_dummy.sendto(readSensorsParam ,(host_robot, port_robot))
 	data, (host, port) = simulator_dummy.recvfrom(1024)

 	try:
 		parametersActions = minidom.parseString(data.replace("\x00", ""))
 		MotorsParam = parametersActions.getElementsByTagName('Actions')
 		#left = MotorsParam[0].attributes['LeftMotor'].value
 		#right = MotorsParam[0].attributes['RightMotor'].value
 	except Exception, e:
 		raise

	
	#---------- Collision On-----------------
	readSensorsParamCollisionOn = '<Measures Time="1234">\
		<Sensors Collision="On">\
		<GPS X="840.5" Y="393.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
		<Buttons Start="On" Stop="Off"/>\
		</Measures>\n'
 	
	simulator_dummy.sendto(readSensorsParamCollisionOn ,(host_robot, port_robot))
 	data, (host, port) = simulator_dummy.recvfrom(1024)	

 	try:
 		parametersActions = minidom.parseString(data.replace("\x00", ""))
 		MotorsParam = parametersActions.getElementsByTagName('Actions')
 		#left = MotorsParam[0].attributes['LeftMotor'].value
 		#right = MotorsParam[0].attributes['RightMotor'].value
 	except Exception, e:
 		raise			
