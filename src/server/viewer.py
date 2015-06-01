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
from settingsChooser import Settings

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
	def main(self, sim_id, remote, sync, starter_c, robotsRegistered_event, simulator_port, hall_of_fame):
		# Load settings
		settings = Settings().getSettings()

		WEBSOCKET_HOST = settings["settings"]["websocket_host"]
		WEBSOCKET_PORT = settings["settings"]["websocket_port"]

		DJANGO_HOST = settings["settings"]["django_host"]
		DJANGO_PORT = settings["settings"]["django_port"]

		REGISTER_ROBOTS_URL = settings["urls"]["register_robots"]

		SIMULATOR_HOST = settings["settings"]["simulator_host"]

		SCORE_URL = settings["urls"]["score"]

		LOG_FILE = settings["settings"]["log_info_file"]

		LOG_FILE += str(simulator_port)
		# End of loading settings

		simulator_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		simulator_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		simulator_s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		simulator_s.connect((SIMULATOR_HOST, simulator_port))
		# Register as PanelViewer in the simulator
		simulator_s.send("<PanelView/>\x04")

		# Get sim time, and ports
		# params, grid e lab comes in this packet as well
		data = simulator_s.recv(8192)
		parametersXML = minidom.parseString("<xml>"+data.split("\x04")[0]+"</xml>")
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

		# Viewer continua a ouvir enquanto o Starter não lhe mandar começar a simulação
		data = None
		data = starter_c.recv()
		robotsXML = minidom.parseString(data)
		robots = robotsXML.getElementsByTagName('Robots')
		robotsAmount = robots[0].attributes['Amount'].value

		print "[VIEWER] Robots Amount:" + robotsAmount

		checkedRobots = []
		prevlen = 0
		while len(checkedRobots) != int(robotsAmount):
			data = simulator_s.recv(8192)
			sr = data.split("\x04")
			if len(sr) <= 1:
				continue
			robotsXML = minidom.parseString(sr[0])
			robots = robotsXML.getElementsByTagName('Robot')
			if len(robots):
				for r in robots:
					robotID = r.attributes['Id'].value
					checkedRobots += [robotID]
					checkedRobots = list(OrderedDict.fromkeys(checkedRobots))
					if len(checkedRobots) != prevlen:
						# Só fazer post se existirem remotos
						data = {'trial_identifier': sim_id,'message': "The robot " + r.attributes['Name'].value + " has registered"}
						response = requests.post("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + REGISTER_ROBOTS_URL, data=data)
					prevlen = len(checkedRobots)
					print "[VIEWER] Robots Registered: " + str(checkedRobots)

		# Robots have registered signal starter
		robotsRegistered_event.set()

		print "[VIEWER] Robots Registered: " + str(len(checkedRobots))

		data = starter_c.recv()
		# while data != "<StartedAgents/>":
		# 	data = starter_c.recv()

		# Sending simulator msg to start the simulation
		simulator_s.send("<Start/>\n\x04")

		if not sync:
			# # Connect to websockets
			websocket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			websocket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			websocket_udp.sendto(sim_id ,(WEBSOCKET_HOST, WEBSOCKET_PORT))

		robotTime = 0
		scoreTime = 0
		number_of_agents_finished = 0
		firstTime = True
		buffer_data = ''
		log_data = []
		while simTime != robotTime:
			# Update Robot time
			data = simulator_s.recv(16384)
			#print data

			sr = data.split("\x04")
			sr[0] = buffer_data + sr[0]
			buffer_data = sr[-1]
			for data in sr[:-1]:
				robotXML = minidom.parseString(data)
				itemlist = robotXML.getElementsByTagName('LogInfo')
				robotTime = itemlist[0].attributes['Time'].value

				if hall_of_fame:
					robotXML = minidom.parseString(data)
					itemlist = robotXML.getElementsByTagName('Leds')
					endLed = itemlist[0].attributes['EndLed'].value

					if endLed == "On":
						number_of_agents_finished += 1
						scoreTime = robotTime

				# Convert to json and write to log file
				json_obj = xmltodict.parse(data, postprocessor=JsonListElements().postprocessorData)
				json_data = json.dumps(json_obj)
				json_data = json_data.replace("@", "_")
				#print json_data
				log_data.append(json_data)

				if not sync:
					# Send data to the websockets
					websocket_udp.sendto(json_data ,(WEBSOCKET_HOST, WEBSOCKET_PORT))

		if not sync:
			websocket_udp.sendto("END" ,(WEBSOCKET_HOST, WEBSOCKET_PORT))

		log_file.write('"Log":[')
		log_file.write(log_data[0])
		for i in range(1,len(log_data)):
			log_file.write(",")
			log_file.write(log_data[i])
		log_file.write("]}")

		starter_c.send('<EndedSimulation/>')

		if hall_of_fame:
			robotXML = minidom.parseString(data)
			itemlist = robotXML.getElementsByTagName('Scores')
			score = itemlist[0].attributes['Score'].value

			if scoreTime == 0:
				scoreTime = simTime

			print "[VIEWER] Posting scores.. score: " + score + " time: " + scoreTime
			# Post score to the end point
			# Type of competition: Hall of Fame - Single
			data = {'trial_id': sim_id, 'score': score, 'number_of_agents': number_of_agents_finished, 'time': scoreTime}
			response = requests.post("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + SCORE_URL, data=data)

			if response.status_code != 201:
				print response.text
				starter_c.send("SCORE-FAIL")
			else:
				starter_c.send("SCORE-SUCCESS")


		# Close all connections
		if not sync:
			websocket_udp.close()

		starter_c.close()
		simulator_s.close()

		# Close all open files
		log_file.close()


