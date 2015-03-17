#encoding=utf-8
import socket
import time
from xml.dom import minidom
from collections import OrderedDict
import json
import xmltodict
import requests

def main():
	## Log File Name
	log_name = "ciberOnline_log.json"

	log = open("log", "w") # log file used to view prints of this program
	log.write("viewer started\n")

	simulator_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	simulator_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	simulator_s.sendto("<View/>\n" ,("127.0.0.1", 6000))
	# Ler o valor do tempo de simulação e obter as portas
	data, (host, port) = simulator_s.recvfrom(4096)
	# Vem params, grid e lab aqui
	parametersXML = minidom.parseString("<xml>"+data.replace("\x00", "")+"</xml>")
	itemlist = parametersXML.getElementsByTagName('Parameters')
	simTime = itemlist[0].attributes['SimTime'].value

	# Write params, grid and lab to the json Log
	log_file = open(log_name, "w")
	data = data.split("<Lab")
	data[1] = "<Lab" + data[1]
	data[1] = data[1].split("<Grid")
	data[1][1] = "<Grid" + data[1][1]

	json_obj = xmltodict.parse(data[0])
	json_data = json.dumps(json_obj, indent=4, separators=(',', ': '))

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	log_file.write(json_data+"\n")

	json_obj = xmltodict.parse(data[1][0])
	json_data = json.dumps(json_obj, indent=4, separators=(',', ': '))

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	log_file.write(json_data+"\n")

	json_obj = xmltodict.parse(data[1][1])
	json_data = json.dumps(json_obj, indent=4, separators=(',', ': '))

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	log_file.write(json_data+"\n")


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
		data, (host, port) = simulator_s.recvfrom(4096)
		#starter_s.send(data)
		#log.write(data)
		robotsXML = minidom.parseString(data.replace("\x00", ""))
		robots = robotsXML.getElementsByTagName('Robot')
		if len(robots):
			for r in robots:
				robotID = r.attributes['Id'].value
				log.write(robotID + "\n	")
				checkedRobots += [robotID]
				checkedRobots = list(OrderedDict.fromkeys(checkedRobots))
				log.write(str(checkedRobots) + "\n	")
				log.write(str(len(checkedRobots)) + "\n")


	log.write("All Robots are registered\n")
	starter_s.send("<AllRobotsRegistered/>")

	data = starter_s.recv(4096)
	while data != "<StartedAgents/>":
		data = starter_s.recv(4096)
	log.write("Received start confirmation")

	simulator_s.sendto("<Start/>\n" ,(host, port))


	PORT = 10000
	django_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	django_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	django_tcp.connect(("127.0.0.1", PORT))

	robotTime = 0
	while simTime != robotTime:
		data = simulator_s.recv(4096)
		# Actualizar o tempo do robot
		data = data.replace("\x00", "")
		#log.write(data)
		robotXML = minidom.parseString(data)
		itemlist = robotXML.getElementsByTagName('LogInfo')
		robotTime = itemlist[0].attributes['Time'].value

		#Convert to json
		json_obj = xmltodict.parse(data)
		json_data = json.dumps(json_obj, indent=4, separators=(',', ': '))

		json_data = json_data.replace("@", "_")
		json_data = json_data.replace('"#text": "\\""', "")

		log_file.write(json_data)

		# Enviar os dados da simulação para o exterior
		django_tcp.send(data)

	#send django msg telling it's over

	starter_s.send('<EndedSimulation LogFile="' + log_name + '" />')

	django_tcp.close()
	log.close()
	log_file.close()
	starter_s.close()
	simulator_s.close()

if __name__ == "__main__":
	main()
