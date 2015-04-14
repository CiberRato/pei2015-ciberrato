import cherrypy
import socket
import re
import json
import subprocess
import netifaces
import time

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

	@cherrypy.expose
	def index(self, **kwargs):

		sim_id = kwargs["simulation_identifier"]

		self.starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.starter_tcp.connect((self.HOST, self.PORT))
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

		if "agent_name" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameters agent_name were expected.")

		agent_name = kwargs["agent_name"]

		AGENT_ENDPOINT = "http://%s:8000/api/v1/competitions/agent_file/%s/" % (DOCKERIP, agent_name,)

		docker = subprocess.Popen("docker run ubuntu/ciberonline " \
									  "bash -c 'curl " \
									  "%s" \
									  " | tar -xz;" \
									  " py.test -x tests.py'" %  \
									  (AGENT_ENDPOINT, ),
									  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		docker.wait()

		return json.dumps({"return code": docker.returncode, "message": "Empty for now.."}, sort_keys=False, \
							indent=4, separators=(',', ': '))

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


# if __name__ == '__main__':
# 	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
# 	settings = json.loads(settings_str)
# 	HOST = settings["settings"]["end_point_host"]
# 	PORT = settings["settings"]["end_point_port"]


# 	cherrypy.config.update({'server.socket_host': HOST ,\
# 							'server.socket_port': PORT })
# 	cherrypy.quickstart(GetSimId(), "/api/v1/simulation_id/")
