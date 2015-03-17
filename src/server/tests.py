# encoding=UTF-8
import pytest
import os.path
import subprocess
import socket
import time
from xml.dom import minidom


def test_fileExists():
	assert os.path.exists('cibertools-v2/robsample/robsample_python.py')

def test_RobotName():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	roboNome = "ciber"
	agentPath = "robsample_python.py"

	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000
	agent = subprocess.Popen(["python", agentPath, "-robname", roboNome], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	nameRobot = robotParam[0].attributes['Name'].value

	assert nameRobot == roboNome


	#para verificar que "esta correcto"
	roboNome = "sdfkb"
	agentPath = "robsample_python.py"

	agent = subprocess.Popen(["python", agentPath, "-robname", roboNome], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	nameRobot = robotParam[0].attributes['Name'].value

	assert nameRobot == roboNome


def test_posicao():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	posicao = "2"
	agentPath = "robsample_python.py"

	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000	
	agent = subprocess.Popen(["python", agentPath, "-pos", posicao], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	ID = robotParam[0].attributes['Id'].value

	assert ID == posicao


	#para verificar que "esta correcto"
	posicao = "1"
	agentPath = "robsample_python.py"

	agent = subprocess.Popen(["python", agentPath, "-pos", posicao], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	ID = robotParam[0].attributes['Id'].value

	assert ID == posicao


def test_host():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	agentPath = "robsample_python.py"
	host = "127.0.0.1"
	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000	
	agent = subprocess.Popen(["python", agentPath, "-host", host], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia
	print host
	host_addr = ""
	try:
	    host_addr = socket.gethostbyname(host)
	    print host_addr
	    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    simulator_dummy.settimeout(1)
	    simulator_dummy.connect((host, port))
	    print host
	    simulator_dummy.close()
	except Exception, e:
		raise

	# result = simulator_dummy.connect_ex(("127.0.0.1", port))
	# print port
	# if result == 0:
	# 	print "Port open"

	# else:
	# 	print "Port ERROR"	

#test_host()


def create_simulator_dummy():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000

def test_Parameters():

	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000
	agentPath = "robsample_python.py"

	agent = subprocess.Popen(["python", agentPath], stdout=subprocess.PIPE)

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
 		left = MotorsParam[0].attributes['LeftMotor'].value
 		right = MotorsParam[0].attributes['RightMotor'].value
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
 		left = MotorsParam[0].attributes['LeftMotor'].value
 		right = MotorsParam[0].attributes['RightMotor'].value
 	except Exception, e:
 		raise	