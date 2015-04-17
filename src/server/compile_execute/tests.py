# encoding=UTF-8
#import pytest
import os.path
import subprocess
import socket
import time
import sys
from xml.dom import minidom

def validate():
	#if not os.path.exists('prepare.sh'):
	if not os.path.exists('execute.sh'):
		error("execute.sh was not found. Use it, otherwise to indicate the proper way to run your files.")
	# I don't want stdout log from compilation, just stderr.
	comp = subprocess.Popen("./prepare.sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, stdout=subprocess.PIPE)
	(stdout, stderr) = comp.communicate() 
	if comp.returncode != 0:
		error(stderr)
	print "Success"
	sys.exit(0)


def error(message):
	sys.stderr.write(message)
	sys.exit(1)

if __name__ == "__main__":
	validate()

def test_executeExists():
	assert os.path.exists('execute.sh')
def test_prepareExists():
	assert os.path.exists('prepare.sh')

def create_simulator():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	return simulator_dummy

def test_RobotName():
	simulator_dummy = create_simulator()
	roboNome = "ciber"
	agentPath = "cibertools-v2.2/robsample/robsample_python.py"

	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000
	#agent = subprocess.Popen(["python", agentPath, "-robname", roboNome], stdout=subprocess.PIPE)
	agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 1 "+roboNome, 
						shell=True, stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	nameRobot = robotParam[0].attributes['Name'].value

	assert nameRobot == roboNome

	#para verificar que "esta correcto"
	roboNome = "sdfkb"
	agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 1 "+roboNome, 
						shell=True, stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	nameRobot = robotParam[0].attributes['Name'].value

	assert nameRobot == roboNome


def test_posicao():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	posicao = "2"
	agentPath = "cibertools-v2.2/robsample/robsample_python.py"

	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000	
	agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 "+posicao+" robot", 
						shell=True, stdout=subprocess.PIPE)
	#agent = subprocess.Popen(["python", agentPath, "-pos", posicao], stdout=subprocess.PIPE)

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	ID = robotParam[0].attributes['Id'].value

	assert ID == posicao


	#para verificar que "esta correcto"
	posicao = "1"

	agent = subprocess.Popen("./prepare.sh; ./execute.sh 127.0.0.1 "+posicao+" robot", 
						shell=True, stdout=subprocess.PIPE)
	
	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	ID = robotParam[0].attributes['Id'].value

	assert ID == posicao


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
