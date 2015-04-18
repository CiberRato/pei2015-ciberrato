import cherrypy
import socket
import re
import json
import subprocess
import netifaces
import time
import requests

class Root(object):
	def __init__(self):
		self.simulation_id = GetSimId()
		self.test_agent = TestAgent()

	@cherrypy.expose
	def index(self):
		return "Eu sou o objecto Raiz"

class GetSimId(object):
	def __init__(self):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)
		self.HOST = settings["settings"]["starter_end_point_host"]
		self.PORT = settings["settings"]["starter_end_point_port"]

		self.starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.starter_tcp.connect((self.HOST, self.PORT))

	@cherrypy.expose
	def index(self, **kwargs):

		sim_id = kwargs["simulation_identifier"]


		self.starter_tcp.send(str(sim_id))

		return "Received sim id:" + str(sim_id)

class TestAgent():
	@cherrypy.expose
	def index(self, **kwargs):
		DOCKERIP = None
		for interface in netifaces.interfaces():
			if interface.startswith('docker'):
				DOCKERIP = netifaces.ifaddresses(interface)[2][0]['addr']
				break
		if DOCKERIP == None:
			print "Please check your docker interface."
			exit(-1)

		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		GET_AGENT_URL = settings["urls"]["get_agent"]

		if "agent_name" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameters agent_name were expected.")

		agent_name = kwargs["agent_name"]

		AGENT_ENDPOINT = "http://%s:8000" + GET_AGENT_URL + "%s/" % (DOCKERIP, agent_name,)

		docker = subprocess.Popen("docker run ubuntu/ciberonline " \
									  "bash -c 'curl -s " \
									  "%s" \
									  " | tar -xz;" \
									  " python tests.py'" %  \
									  (AGENT_ENDPOINT, ),
									  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdout, stderr) = docker.communicate()
		if docker.returncode != 0:
			message = stderr
		else:
			message = "Passed tests with success"

		url = "http://localhost:8000/api/v1/agents/code_validation/"+agent_name+"/"
		data = {'code_valid': docker.returncode == 0, 'validation_result': message}
		requests.put(url, data=data)

class EndPoint():
	def start(self):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		HOST = settings["settings"]["end_point_host"]
		PORT = settings["settings"]["end_point_port"]

		config = {'global':
		    {
		        'server.socket_host': str(HOST),
		        'server.socket_port': PORT,
		    }
		}

		cherrypy.quickstart(Root(), "/api/v1/", config)

