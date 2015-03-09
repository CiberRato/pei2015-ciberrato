#encoding=utf-8
import socket
import time
from xml.dom import minidom
from collections import OrderedDict
import json

def main():
	log_name = "ciberOnline_log"
	log = open("log.txt", "w") # log file used to view prints of this program
	log.write("viewer started")

	simulator_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	simulator_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	simulator_s.sendto("<View/>\n" ,("127.0.0.1", 6000))
	# Ler o valor do tempo de simulação e obter as portas
	data, (host, port) = simulator_s.recvfrom(1024)
	parametersXML = minidom.parseString(data.replace("\x00", ""))
	itemlist = parametersXML.getElementsByTagName('Parameters')
	simTime = itemlist[0].attributes['SimTime'].value
	log.write("SimTime: "+ simTime+"\n")

	log_file = open(log_name, "w")
	log_file.write(data)

	starter_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	starter_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	starter_s.connect(("127.0.0.1", 7000))

	# Viewer continua a ouvir enquanto o Starter não lhe mandar começar a simulação
	data = starter_s.recv(4096)
	robotsXML = minidom.parseString(data)
	robots = robotsXML.getElementsByTagName('Robots')
	robotsAmount = robots[0].attributes['Amount'].value

	log.write("Robots Amount: " + robotsAmount + "\n")

	log.write("checking Robots\n")

	checkedRobots = []
	while len(checkedRobots) != int(robotsAmount):
		data, (host, port) = simulator_s.recvfrom(1024)
		#starter_s.send(data)
		robotsXML = minidom.parseString(data.replace("\x00", ""))
		robots = robotsXML.getElementsByTagName('Robot')
		if len(robots):
			robotID = robots[0].attributes['Id'].value
			log.write(robotID + "\n	")
			checkedRobots += [robotID]
			checkedRobots = list(OrderedDict.fromkeys(checkedRobots))
			log.write(str(checkedRobots) + "\n	")
			#log.write(str(len(checkedRobots)) + "\n")


	log.write("All Robots are registered\n")
	starter_s.send("<AllRobotsRegistered/>")

	data = starter_s.recv(4096)
	while data != "<StartedAgents/>":
		data = starter_s.recv(4096)
	simulator_s.sendto("<Start/>\n" ,(host, port))

	robotTime = 0
	#django_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#django_tcp.bind(("127.0.0.1", 7000))
	#django_tcp.listen(1)
	#django_s, django_addr = django_tcp.accept()
	jsonFile = open("test.json", "w")
	while simTime != robotTime:
		data = simulator_s.recv(4096)
		# Actualizar o tempo do robot
		data = data.replace("\x00", "")
		robotXML = minidom.parseString(data)
		itemlist = robotXML.getElementsByTagName('Robot')
		robotTime = itemlist[0].attributes['Time'].value

		#Convert to json
		robot_json = json.dumps(robotXML, skipkeys=True)

		# Enviar os dados da simulação para o exterior
		#django_s.send(data)
		log_file.write(robot_json)

	starter_s.send("<EndedSimulation/>")

	starter_s.close()
	simulator_s.close()

if __name__ == "__main__":
	main()
