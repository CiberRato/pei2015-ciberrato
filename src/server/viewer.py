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

class JsonListElements:
	# Listar em cada self.grid, self.param, etc.. os parametros que podem ser listas!
	def __init__(self):
		self.prevPath = None
		self.count = 0
		self.list = None
		self.lab = {'Corner': None, 'Wall': None, 'Beacon': None, 'Target': None}
		self.grid = {'Position': None}
		self.params = {}
		self.data = {'Robot': None, 'IRSensor': None}

	# Só para evitar verificar demasiadas keys
	def postprocessorGrid(self, path, key, value):
		self.list = self.grid
		return self.postprocessor(path, key, value)
	def postprocessorLab(self, path, key, value):
		self.list = self.lab
		return self.postprocessor(path, key, value)
	def postprocessorParams(self, path, key, value):
		self.list = self.params
		return self.postprocessor(path, key, value)
	def postprocessorData(self, path, key, value):
		self.list = self.data
		return self.postprocessor(path, key, value)

	def postprocessor(self, path, key, value):
		if key in self.list.keys() and self.list[key] == None:
			self.list[key] = len(path)
			tupl = key, [value]
		else:
			tupl = key, value

		for key in self.list.keys():
			if self.list[key] != None and self.list[key] > len(path):
				self.list[key] = None
		return tupl

class Viewer:
	def main(self, sim_id):
		# Load settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		SIMULATOR_HOST = settings["settings"]["simulator_host"]
		SIMULATOR_PORT = settings["settings"]["simulator_port"]

		STARTER_HOST = settings["settings"]["starter_viewer_host"]
		STARTER_PORT = settings["settings"]["starter_viewer_port"]

		WEBSOCKET_HOST = settings["settings"]["websocket_host"]
		WEBSOCKET_PORT = settings["settings"]["websocket_port"]

		DJANGO_HOST = settings["settings"]["django_host"]
		DJANGO_PORT = settings["settings"]["django_port"]

		REGISTER_ROBOTS_URL = settings["urls"]["register_robots"]

		LOG_FILE = settings["settings"]["log_info_file"]
		# End of loading settings

		simulator_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		simulator_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Register as PanelViewer in the simulator
		simulator_s.sendto("<PanelView/>\n" ,(SIMULATOR_HOST, SIMULATOR_PORT))

		# Get sim time, and ports
		# params, grid e lab comes in this packet as well
		data, (hostSim, portSim) = simulator_s.recvfrom(4096)
		parametersXML = minidom.parseString("<xml>"+data.replace("\x00", "")+"</xml>")
		itemlist = parametersXML.getElementsByTagName('Parameters')
		simTime = itemlist[0].attributes['SimTime'].value

		# Log file to be written
		log_file = open(LOG_FILE, "w")

		parameters = itemlist[0].toxml()
		lab = parametersXML.getElementsByTagName('Lab')[0].toxml()
		grid = parametersXML.getElementsByTagName('Grid')[0].toxml()

		# Write parameters
		json_obj = xmltodict.parse(parameters, postprocessor=JsonListElements().postprocessorParams)
		json_data = json.dumps(json_obj)

		json_data = json_data.replace("@", "_")
		json_data = json_data.replace('"#text": "\\""', "")

		log_file.write("{"+json_data[1:-1]+",")

		# Write lab
		json_obj = xmltodict.parse(lab, postprocessor=JsonListElements().postprocessorLab)
		json_data = json.dumps(json_obj)

		json_data = json_data.replace("@", "_")
		json_data = json_data.replace('"#text": "\\""', "")

		log_file.write(json_data[1:-1]+",")

		# Write grid
		json_obj = xmltodict.parse(grid, postprocessor=JsonListElements().postprocessorGrid)
		json_data = json.dumps(json_obj)

		json_data = json_data.replace("@", "_")
		json_data = json_data.replace('"#text": "\\""', "")

		log_file.write(json_data[1:-1]+",")


		starter_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		starter_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		starter_s.connect((STARTER_HOST, STARTER_PORT))

		# Viewer continua a ouvir enquanto o Starter não lhe mandar começar a simulação
		data = starter_s.recv(4096)
		robotsXML = minidom.parseString(data)
		robots = robotsXML.getElementsByTagName('Robots')
		robotsAmount = robots[0].attributes['Amount'].value

		print "[VIEWER] Robots Amount:" + robotsAmount + "\n"

		checkedRobots = []
		prevlen = 0
		while len(checkedRobots) != int(robotsAmount):
			data, (host, port) = simulator_s.recvfrom(4096)
			robotsXML = minidom.parseString(data.replace("\x00", ""))
			robots = robotsXML.getElementsByTagName('Robot')
			if len(robots):
				for r in robots:
					robotID = r.attributes['Id'].value
					checkedRobots += [robotID]
					checkedRobots = list(OrderedDict.fromkeys(checkedRobots))
					if len(checkedRobots) != prevlen:
						data = {'trial_identifier': sim_id,'message': "The robot " + r.attributes['Name'].value + " has registered"}
						response = requests.post("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + REGISTER_ROBOTS_URL, data=data)
					prevlen = len(checkedRobots)
					print "[VIEWER] Robots Registered: " + str(checkedRobots)

		starter_s.send("<RobotsRegistered/>")

		print "[VIEWER] Robots Registered: " + str(len(checkedRobots))

		data = starter_s.recv(4096)
		while data != "<StartedAgents/>":
			data = starter_s.recv(4096)

		# Sending simulator msg to start the simulation
		simulator_s.sendto("<Start/>\n" ,(hostSim, portSim))

		# Connect to websockets
		websocket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		websocket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		websocket_tcp.connect((WEBSOCKET_HOST, WEBSOCKET_PORT))

		robotTime = 0
		firstTime = True
		log_file.write('"Log":[')
		while simTime != robotTime:
			# Update Robot time
			data = simulator_s.recv(4096)
			data = data.replace("\x00", "")
			robotXML = minidom.parseString(data)
			itemlist = robotXML.getElementsByTagName('LogInfo')
			robotTime = itemlist[0].attributes['Time'].value

			# Convert to json and write to log file
			json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorData)
			json_data = json.dumps(json_obj)
			json_data = json_data.replace("@", "_")

			if not firstTime:
				if int(robotTime) != 0:
					log_file.write(",")
					log_file.write(json_data)
					# Send data to the websockets
					websocket_tcp.send(json_data)
			else:
				firstTime = False
				log_file.write(json_data)
				# Send data to the websockets
				websocket_tcp.send(json_data)



		log_file.write("]}")

		# Wait 0.1 seconds to assure the END msg goes on a separate packet
		time.sleep(0.1)
		# Send websocket msg telling it's over
		websocket_tcp.send("END")

		starter_s.send('<EndedSimulation/>')

		# Close all connections
		websocket_tcp.close()
		starter_s.close()
		simulator_s.close()

		# Close all open files
		log_file.close()

# if __name__ == "__main__":
# 	main()
