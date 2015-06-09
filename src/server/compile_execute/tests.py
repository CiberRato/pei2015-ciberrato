# encoding=UTF-8
import os.path, subprocess, socket, time, sys
# Replace this with from enum import Enum with python 3.4
from flufl.enum import Enum
from xml.dom import minidom

class ValidatorMessage(Enum):
	"""
	This class represents an enumerate.
	Where the first element is the ID of the message and 
	the second element is the message.
	"""
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
		"""
		Class constructor
		Arguments:
			code - the error code identifier.
			message - the details about the error message.
		"""
		self._code = code
		self._message = message

def error(vmsg, stdout_err = None):
	"""
	This function shuts down the unit testing.
	Arguments:
		vmsg - Message that is going to be printed as an error.
		stdout_err - Stdout/Stderr if available.
	"""
	if stdout_err == None:
		sys.stderr.write(vmsg.value[1])
	else:
		sys.stderr.write(vmsg.value[1] + "\nAgent standard output/error:\n" + stdout_err)
	sys.exit(vmsg.value[0])

class Validator:
	"""
	Class responsible for make the proper tests to the robot.
	"""
	def __init__(self):
		pass

	def validate(self):
		"""
		Main function that is responsible for calling and make minor 
		verifications. It starts by checking if execute.sh and prepare.sh 
		exist, after that it calls more specific functions.
		"""
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
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			(stdout, stderr) = comp.communicate()
			if comp.returncode != 0:
				error(ValidatorMessage.FAILED_PREPARE, stdout.read())

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

		#self.validateMessagesExchanged()
		sys.exit(0)

	def validateRobotName(self, name):
		"""
		This function creates a dummy server and waits for a robot message 
		to register. It verifies if it is possible to change the robot name 
		using the execute.sh
		"""
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 1 "+name, 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		try:
			client_s, client_addr = simulator_dummy.accept()
			client_s.settimeout(1)
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT, agent.stdout.read())
			

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

		try:
			parametersXML = minidom.parseString(data.split("\x04")[0])
			robotParam = parametersXML.getElementsByTagName('Robot')
			nameRobot = robotParam[0].attributes['Name'].value

			if nameRobot != name:
				error(ValidatorMessage.ROBOTNAME, agent.stdout.read())
		except:
			error(ValidatorMessage.REGISTER_MESSAGE, agent.stdout.read())

	def validatePosition(self, pos):
		"""
		This function creates a dummy server and waits for a robot message 
		to register. It verifies if it is possible to change the robot position
		using the execute.sh
		"""
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 "+pos+" robot", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		try:
			client_s, client_addr = simulator_dummy.accept()
			client_s.settimeout(1)
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT, agent.stdout.read())

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

		try:
			parametersXML = minidom.parseString(data.split("\x04")[0])
			robotParam = parametersXML.getElementsByTagName('Robot')
			ID = robotParam[0].attributes['Id'].value

			if ID != pos:
				error(ValidatorMessage.POSITION, agent.stdout.read())
		except:
			error(ValidatorMessage.REGISTER_MESSAGE, agent.stdout.read())

	def validateHost(self, hostVal):
		"""
		This function creates a dummy server and waits for a robot message 
		to register. It verifies if it is possible to change the host 
		where the server is registered using the execute.sh
		"""
		hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		hostSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		hostSocket.bind((hostVal, 6000))
		hostSocket.settimeout(1)
		hostSocket.listen(1)

		agent = subprocess.Popen("./execute.sh "+hostVal+" 1 robot",
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		try:
			client_s, client_addr = hostSocket.accept()
			client_s.settimeout(1)
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT, agent.stdout.read())

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
		"""
		This function creates a dummy server and waits for a robot message to 
		register. It will validate every message exchange between the 
		simulator and the robot, like Actions and Measures.
		"""
		simulator_dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_dummy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_dummy.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		simulator_dummy.bind(("127.0.0.1", 6000))
		simulator_dummy.settimeout(1)
		simulator_dummy.listen(1)

		agent = subprocess.Popen("./execute.sh 127.0.0.1 1 robot", 
				shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		try:
			client_s, client_addr = simulator_dummy.accept()
			client_s.settimeout(1)
			data = client_s.recv(1024) # infos de quem envia
		except socket.timeout:
			error(ValidatorMessage.TIMEOUT, agent.stdout.read())
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
			error(ValidatorMessage.ANSWER_ACTIONS, agent.stdout.read())

		try:
			parametersActions = minidom.parseString(data.split("\x04")[0])
			MotorsParam = parametersActions.getElementsByTagName('Actions')
		except:
			error(ValidatorMessage.VALID_ACTIONS, agent.stdout.read())

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
			error(ValidatorMessage.ANSWER_ACTIONS, agent.stdout.read())	

		try:
			parametersActions = minidom.parseString(data.split("\x04")[0])
			MotorsParam = parametersActions.getElementsByTagName('Actions')
		except:
			error(ValidatorMessage.NOT_ACTIONS, agent.stdout.read())

		agent.kill()
		client_s.close()
		simulator_dummy.shutdown(socket.SHUT_RDWR)
		simulator_dummy.close()

if __name__ == "__main__":
	Validator().validate()