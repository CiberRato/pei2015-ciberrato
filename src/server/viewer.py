#encoding=utf-8
import socket
import time
import json
import xmltodict
import requests
import re
import sys
from xml.dom import minidom
from collections import OrderedDict

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def main():
	wlog = False
	for i in range(0, len(sys.argv)):
		if sys.argv[i] == "-log":
			wlog = True
	#Load settings
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)

	TIMEOUT = settings["settings"]["timeout"]

	SIMULATOR_HOST = settings["settings"]["simulator_host"]
	SIMULATOR_PORT = settings["settings"]["simulator_port"]

	STARTER_HOST = settings["settings"]["starter_viewer_host"]
	STARTER_PORT = settings["settings"]["starter_viewer_port"]

	WEBSOCKET_HOST = settings["settings"]["websocket_host"]
	WEBSOCKET_PORT = settings["settings"]["websocket_port"]

	LOG_FILE = settings["settings"]["log_info_file"]
	PARAM_FILE = settings["settings"]["params_file"]
	LAB_FILE = settings["settings"]["lab_file"]
	GRID_FILE = settings["settings"]["grid_file"]
	#end of loading settings

	if wlog:
		log = open("log", "w") # log file used to view prints of this program
		log.write("viewer started\n")

	simulator_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	simulator_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	simulator_s.sendto("<PanelView/>\n" ,(SIMULATOR_HOST, SIMULATOR_PORT))
	# Ler o valor do tempo de simulação e obter as portas
	data, (hostSim, portSim) = simulator_s.recvfrom(4096)
	# Vem params, grid e lab aqui
	parametersXML = minidom.parseString("<xml>"+data.replace("\x00", "")+"</xml>")
	itemlist = parametersXML.getElementsByTagName('Parameters')
	simTime = itemlist[0].attributes['SimTime'].value

	# Write params, grid and lab to the json Log
	log_file = open(LOG_FILE, "w")
	params_file = open(PARAM_FILE, "w")
	lab_file = open(LAB_FILE, "w")
	grid_file = open(GRID_FILE, "w")


	parameters = itemlist[0].toxml()
	lab = parametersXML.getElementsByTagName('Lab')[0].toxml()
	grid = parametersXML.getElementsByTagName('Grid')[0].toxml()

	json_obj = xmltodict.parse(parameters)
	json_data = json.dumps(json_obj)

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	#params_file.write(json_data)
	log_file.write("{"+json_data[1:-1]+",")


	json_obj = xmltodict.parse(lab)
	json_data = json.dumps(json_obj)

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	#lab_file.write(json_data)
	log_file.write(json_data[1:-1]+",")


	json_obj = xmltodict.parse(grid)
	json_data = json.dumps(json_obj)

	json_data = json_data.replace("@", "_")
	json_data = json_data.replace('"#text": "\\""', "")
	#grid_file.write(json_data)
	log_file.write(json_data[1:-1]+",")


	starter_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	starter_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	starter_s.connect((STARTER_HOST, STARTER_PORT))

	# Viewer continua a ouvir enquanto o Starter não lhe mandar começar a simulação
	data = starter_s.recv(4096)
	robotsXML = minidom.parseString(data)
	robots = robotsXML.getElementsByTagName('Robots')
	robotsAmount = robots[0].attributes['Amount'].value

	if wlog:
		log.write("Robots Amount: " + robotsAmount + "\n")
		log.write("checking Robots\n")

	count = 0
	checkedRobots = []
	while len(checkedRobots) != int(robotsAmount) or count > TIMEOUT:
		count += 1
		data, (host, port) = simulator_s.recvfrom(4096)
		if wlog:
			log.write(data + "\n")
		robotsXML = minidom.parseString(data.replace("\x00", ""))
		robots = robotsXML.getElementsByTagName('Robot')
		if len(robots):
			for r in robots:
				robotID = r.attributes['Id'].value
				if wlog:
					log.write(robotID + "\n	")
				checkedRobots += [robotID]
				checkedRobots = list(OrderedDict.fromkeys(checkedRobots))
				if wlog:
					log.write(str(checkedRobots) + "\n	")
					log.write(str(len(checkedRobots)) + "\n")
	if wlog:
		log.write("RobotsRegistered=%s\n", str(len(checkedRobots)))

	starter_s.send('<Robots Registered="' + str(len(checkedRobots)) + '"/>')

	data = starter_s.recv(4096)
	while data != "<StartedAgents/>":
		data = starter_s.recv(4096)

	if wlog:
		log.write("Received start confirmation\n")

	simulator_s.sendto("<Start/>\n" ,(hostSim, portSim))



	websocket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	websocket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	websocket_tcp.connect((WEBSOCKET_HOST, WEBSOCKET_PORT))

	robotTime = 0

	firstTime = True
	log_file.write('"Log":[')
	while simTime != robotTime:
		if not firstTime:
			log_file.write(",")
		else:
			firstTime = False
		data = simulator_s.recv(4096)
		# Actualizar o tempo do robot
		data = data.replace("\x00", "")
		if wlog:
			log.write(data + "\n")
		robotXML = minidom.parseString(data)
		itemlist = robotXML.getElementsByTagName('LogInfo')
		robotTime = itemlist[0].attributes['Time'].value

		#Convert to json
		json_obj = xmltodict.parse(data)
		json_data = json.dumps(json_obj)
		json_data = json_data.replace("@", "_")
		#json_data = json_data.replace('"#text": "\\""', "")

		log_file.write(json_data)

		# Enviar os dados da simulação para o exterior
		#print json_data
		websocket_tcp.send(json_data)

	log_file.write("]}")

	#wait 0.1 seconds to assure the END msg goes on a separate packet
	time.sleep(0.1)
	#send websocket msg telling it's over
	websocket_tcp.send("END")

	starter_s.send('<EndedSimulation/>')

	if wlog:
		log.close()
	websocket_tcp.close()
	log_file.close()
	params_file.close()
	lab_file.close()
	grid_file.close()
	starter_s.close()
	simulator_s.close()

if __name__ == "__main__":
	main()
