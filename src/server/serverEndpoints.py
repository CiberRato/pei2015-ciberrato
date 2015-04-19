import cherrypy, socket, re, json, subprocess, netifaces, time, requests
from multiprocessing import Process

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

		self.starter_tcp.send("sim_id="+str(sim_id))
		return "Received sim id:" + str(sim_id)

class TestAgent():
	def __init__(self):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)
		self.HOST = settings["settings"]["test_end_point_host"]
		self.PORT = settings["settings"]["test_end_point_port"]

		self.tests_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tests_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tests_tcp.connect((self.HOST, self.PORT))

	@cherrypy.expose
	def index(self, **kwargs):
		if "agent_name" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameters agent_name were expected.")

		agent_name = kwargs["agent_name"]

		self.tests_tcp.send("agent_name="+str(agent_name))
		return "Received test request for agent " + str(agent_name)

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

