# encoding=UTF-8
import os.path, subprocess, socket, time, sys
# Replace this with from enum import Enum with python 3.4
from flufl.enum import Enum
from xml.dom import minidom

class ValidatorMessage(Enum):
	EXEC_MISSING 		= (1, "execute.sh was not found. Use it, otherwise to indicate the proper way to run your files.")
	FAILED_PREPARE 		= (2, "Failed to execute prepare.sh")
	TIMEOUT 			= (3, "Simulator will not be able to receive answer, please check host parameter, agent port and execute.sh.")
	ROBOTNAME 			= (4, "execute.sh doesn't allow to change agent name.\n"
								"Please check that the third parameter on execute.sh should be able to change agent name.")
	POSITION 			= (5, "execute.sh doesn't allow to change robot position.\n"
								"Please check that the second parameter on execute.sh should be able to change agent position.")
	ROBOTID 			= (6, "Message registering agent sent has an invalid robot id.")
	REGISTER_MESSAGE 	= (7, "Message registering agent sent to the simulator is not valid.")
	ANSWER_ACTIONS 		= (8, "Messages sent to the simulator with the actions failed to receive.")
	VALID_ACTIONS 		= (9, "Messages received after the Measures is not an valid actions message. Please check it.")
	NOT_ACTIONS 		= (10, "Messages received after the Measures is not an Actions. Please check it.")

	def __init__(self, code, message):
		self._code = code
		self._message = message

def error(vmsg, additional_info = None):
	if additional_info == None:
		sys.stderr.write(vmsg.value[1])
	else:
		sys.stderr.write(vmsg.value[1] + "\n" + additional_info)
	sys.exit(vmsg.value[0])

class Validator:
	def __init__(self):
		pass

	def validate(self):
		if not os.path.exists('execute.sh'):
			error(ValidatorMessage.EXEC_MISSING)
		else:
			sub = subprocess.Popen("chmod +x execute.sh", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sub.wait()
		# I don't want stdout log from compilation, just stderr.
		# Bash -e -o pipefail will check for return codes in every single line.
		if os.path.exists('prepare.sh'):
			comp = subprocess.Popen("chmod +x prepare.sh; bash -e -o pipefail prepare.sh", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(stdout, stderr) = comp.communicate()
			if comp.returncode != 0:
				error(ValidatorMessage.FAILED_PREPARE, stderr)

		## At this point we got every file compiled, or at least, it should be.
		# Lets make sure that everything is ready!
		# Testing robot names parameter
		self.validateRobotName("myrobot")
		self.validateRobotName("thisisaaname")
		# Testing position paramter
		self.validatePosition("1")
		self.validatePosition("5")
		# Testing host paramter
		self.validateHost("127.0.0.20")
		self.validateHost("127.0.0.33")

		self.validateMessagesExchanged()
		sys.exit(0)

	def validateRobotName(self, name):
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 1 "+name, 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			client_s, client_addr = simulator_dummy.accept()
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT)

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

		try:
			parametersXML = minidom.parseString(data.split("\x04")[0])
			robotParam = parametersXML.getElementsByTagName('Robot')
			nameRobot = robotParam[0].attributes['Name'].value

			if nameRobot != name:
				error(ValidatorMessage.ROBOTNAME)
		except:
			error(ValidatorMessage.REGISTER_MESSAGE)

	def validatePosition(self, pos):
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 "+pos+" robot", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		try:
			client_s, client_addr = simulator_dummy.accept()
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT)

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

		try:
			parametersXML = minidom.parseString(data.split("\x04")[0])
			robotParam = parametersXML.getElementsByTagName('Robot')
			ID = robotParam[0].attributes['Id'].value

			if ID != pos:
				error(ValidatorMessage.POSITION)
		except:
			error(ValidatorMessage.REGISTER_MESSAGE)

	def validateHost(self, hostVal):
		hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		hostSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		hostSocket.bind((hostVal, 6000))
		hostSocket.settimeout(1)
		hostSocket.listen(1)

		agent = subprocess.Popen("./execute.sh "+hostVal+" 1 robot",
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			client_s, client_addr = hostSocket.accept()
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT)

		agent.kill()
		client_s.close()
		hostSocket.shutdown(socket.SHUT_RDWR)
		hostSocket.close()

		try:
			parametersXML = minidom.parseString(data.split("\x04")[0])
			robotParam = parametersXML.getElementsByTagName('Robot')
			robotid = robotParam[0].attributes['Id']
			if int(robotid.value) < 0:
				error(ValidatorMessage.ROBOTID)
			robotName = robotParam[0].attributes['Name']
		except:
			error(ValidatorMessage.REGISTER_MESSAGE)

	def validateMessagesExchanged(self):
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 1 robot", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			client_s, client_addr = simulator_dummy.accept()
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT)
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
			TargetReward="100" HomeReward="100" /></Reply>\n\x04'	

		# Simulating the answer to the agent..	
		client_s.send(parameters)
		time.sleep(0.5)

		readSensorsParam = '<Measures Time="345">\
			<Sensors Collision="No">\
			<GPS X="845.5" Y="403.6" />\
			</Sensors>\
			<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
			<Buttons Start="On" Stop="Off"/>\
			</Measures>\n\x04'
		
		client_s.send(readSensorsParam)
		# Simulating a Measures to the agent...
		#self.simulator_dummy.sendto(readSensorsParam ,(host_robot, port_robot))

		try:
	 		data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.ANSWER_ACTIONS)

		try:
			parametersActions = minidom.parseString(data.split("\x04")[0])
			MotorsParam = parametersActions.getElementsByTagName('Actions')
		except:
			error(ValidatorMessage.VALID_ACTIONS)

		# More measures
		readSensorsParamCollisionOn = '<Measures Time="1234">\
			<Sensors Collision="On">\
			<GPS X="840.5" Y="393.6" />\
			</Sensors>\
			<Leds EndLed="Off" ReturningLed="Off" VisitingLed="Off"/>\
			<Buttons Start="On" Stop="Off"/>\
			</Measures>\n\x04'
		
		client_s.send(readSensorsParamCollisionOn)
		try:
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.ANSWER_ACTIONS)	

		try:
			parametersActions = minidom.parseString(data.split("\x04")[0])
			MotorsParam = parametersActions.getElementsByTagName('Actions')
		except:
			error(ValidatorMessage.NOT_ACTIONS)

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

if __name__ == "__main__":
	Validator().validate()