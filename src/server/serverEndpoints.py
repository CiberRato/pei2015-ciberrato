import cherrypy, socket, re, json, subprocess, netifaces, time, requests
from multiprocessing import Process
from settingsChooser import Settings

class Root(object):
	def __init__(self):
		self.trials = Services()

		settings = Settings().getSettings()
		self.HOST = settings["settings"]["starter_end_point_host"]
		self.PORT = settings["settings"]["starter_end_point_port"]

		self.starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.starter_tcp.connect((self.HOST, self.PORT))

	@cherrypy.expose
	def trial_id(self, **kwargs):
		if "trial_identifier" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameter trial_identifier was expected.")

		sim_id = kwargs["trial_identifier"]

		self.starter_tcp.send("sim_id="+str(sim_id))
		return "Received sim id:" + str(sim_id)

	@cherrypy.expose
	def test_agent(self, **kwargs):
		if "agent_name" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameter agent_name was expected.")

		agent_name = kwargs["agent_name"]
		team_name = kwargs["team_name"]
		team_name = team_name.replace("/", "")

		self.starter_tcp.send("team_name=" + str(team_name) + "&" + "agent_name="+str(agent_name))
		return "Received test request for agent " + str(agent_name)


class Services(object):
	def __init__(self):
		pass

	@cherrypy.expose
	def start(self, **kwargs):
		if "trial_identifier" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameter trial_identifier was expected.")

		trial_id = kwargs["trial_identifier"]

		settings = Settings().getSettings()
		HOST = settings["settings"]["services_end_point_host"]
		PORT = settings["settings"]["services_end_point_port"]

		starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		starter_tcp.connect((HOST, PORT))

		starter_tcp.send("start="+trial_id)

		return "trial=" + trial_id


class EndPoint():
	def start(self):
		settings = Settings().getSettings()

		HOST = settings["settings"]["end_point_host"]
		PORT = settings["settings"]["end_point_port"]

		config = {'global':
		    {
		        'server.socket_host': str(HOST),
		        'server.socket_port': PORT,
		    }
		}

		cherrypy.quickstart(Root(), "/api/v1/", config)


