#encoding=utf-8
import socket
import time
from xml.dom import minidom
import subprocess

import os.path
os.path.exists('cibertools-v2/robsample/robsample_python.py') # verificar se ficheiro existe

def main():
	simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # comunicação UDP
	simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	simulator_dummy.bind(("127.0.0.1", 6000)) # ouvir na porta 6000

	agentPath = "cibertools-v2.2/robsample/robsample_python.py"
	posicao = "5"
	host = "127.0.0.1"
	roboNome = "gabriel"


	agent = subprocess.Popen(["python", agentPath, "-host", host, "-pos", posicao, "-robname", roboNome], stdout=subprocess.PIPE)
		# subprocesso para abrir processos

	data, (host, port) = simulator_dummy.recvfrom(1024) # infos de quem envia

	print data
	print host

	
	parametersXML = minidom.parseString(data.replace("\x00", ""))
	robotParam = parametersXML.getElementsByTagName('Robot')
	ID = robotParam[0].attributes['Id'].value
	print "ID:", ID

	nameRobot = robotParam[0].attributes['Name'].value
	print "Name:",nameRobot

	if ID != posicao:
		print "ERROR: Robot ID"
		exit()

	
	if nameRobot != roboNome:
		print "ERROR: Wrong Robot Name"
		exit()

	

	print "passou"	

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
		TargetReward="100" HomeReward="100"\
		/>'
	
	simulator_dummy.sendto(parameters ,("127.0.0.1", port))

#------------------------1º teste-----------------------------------
	readSensorsParam = '<Measures Time="0">\
		<Sensors Collision="No">\
		<GPS X="845.5" Y="403.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
		<Buttons Start="Off" Stop="On"/>\
		</Measures>'

	simulator_dummy.sendto(readSensorsParam ,("127.0.0.1", port))
	
#----------------------------2º teste---------------------	
	data, (host, port) = simulator_dummy.recvfrom(1024);

	readSensorsParam = '<Measures Time="234">\
		<Sensors Collision="No">\
		<GPS X="845.5" Y="403.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
		<Buttons Start="On" Stop="Off"/>\
		</Measures>'

	simulator_dummy.sendto(readSensorsParam ,("127.0.0.1", port))

#----------------------3ºteste----------------------------	
	data, (host, port) = simulator_dummy.recvfrom(1024);

	readSensorsParam = '<Measures Time="100">\
		<Sensors Collision="On">\
		<GPS X="845.5" Y="403.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
		<Buttons Start="On" Stop="Off"/>\
		</Measures>'

	simulator_dummy.sendto(readSensorsParam ,("127.0.0.1", port))

#---------------------------------------------------------------------

	data, (host, port) = simulator_dummy.recvfrom(1024);

	readSensorsParam = '<Measures Time="1000">\
		<Sensors Collision="Off">\
		<GPS X="845.5" Y="403.6" />\
		</Sensors>\
		<Leds EndLed="Off" ReturningLed="Off" VisitingLed="On"/>\
		<Buttons Start="On" Stop="Off"/>\
		</Measures>'

	simulator_dummy.sendto(readSensorsParam ,("127.0.0.1", port))

#	--------------------------------------------------------------


	data, (host, port) = simulator_dummy.recvfrom(1024)

	driveMotorsValues = '<Actions LeftMotor="0.1" RightMotor="0.1"/>'
	simulator_dummy.sendto(driveMotorsValues, ("127.0.0.1", port))

# -----------------------visiting LedON-----------------------

	data, (host, port) = simulator_dummy.recvfrom(1024)

	visitingledON = '<Actions LeftMotor="0.0" RightMotor="0.0" VisitingLed="On"/>'
	simulator_dummy.sendto(visitingledON, ("127.0.0.1", port))


# ------------------------visiting LedOff----------------------
	data, (host, port) = simulator_dummy.recvfrom(1024)

	visitingledOff = '<Actions LeftMotor="0.1" RightMotor="0.1" VisitingLed="Off"/>'
	simulator_dummy.sendto(visitingledOff, ("127.0.0.1", port))


# ------------------Finish-------------------------------------
	data, (host, port) = simulator_dummy.recvfrom(1024)

	finishParam = '<Actions LeftMotor="0.0" RightMotor="0.0" EndLed="On"/>'
	simulator_dummy.sendto(finishParam, ("127.0.0.1", port))	


# ---------------returning ledOn --------------------------

	data, (host, port) = simulator_dummy.recvfrom(1024)

	returnOnParam = '<Actions LeftMotor="0.0" RightMotor="0.0" ReturningLed="On"/>'
	simulator_dummy.sendto(returnOnParam, ("127.0.0.1", port))

# ------------returning ledOff----------------------

	data, (host, port) = simulator_dummy.recvfrom(1024)

	returnOffParam = '<Actions LeftMotor="0.1" RightMotor="0.1" ReturningLed="Off"/>'
	simulator_dummy.sendto(returnOffParam, ("127.0.0.1", port))
		
		# # Ler o valor do tempo de simulação e obter as portas
	# data, (host, port) = simulator_s.recvfrom(1024)
	# parametersXML = minidom.parseString(data.replace("\x00", ""))
	# itemlist = parametersXML.getElementsByTagName('Parameters') 
	# simTime = itemlist[0].attributes['SimTime'].value
	# print "SimTime: ", simTime

	# # Viewer continua a ouvir enquanto o Starter não lhe mandar começar a simulação
	
	agent.terminate()
	agent.wait()
	simulator_dummy.close()


if __name__ == "__main__":
	main()
