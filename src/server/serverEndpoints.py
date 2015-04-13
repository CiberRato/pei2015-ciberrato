import cherrypy
import socket
import re
import json

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
		HOST = settings["settings"]["starter_end_point_host"]
		PORT = settings["settings"]["starter_end_point_port"]

	@cherrypy.expose
	def index(self, **kwargs):

		sim_id = kwargs["simulation_identifier"]

		self.starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.starter_tcp.connect((HOST, PORT))
		self.starter_tcp.send(str(sim_id))

		return "Received sim id:" + str(sim_id)

class TestAgent():
	@cherrypy.expose
	def index(self, **kwargs):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		if "simulation_identifier" not in kwargs or "agent_name" not in kwargs:
			raise cherrypy.HTTPError(400, "Parameters simulation_identifier and agent_name were expected.")
		
		sim_id = kwargs["simulation_identifier"]
		agent_name = kwargs["agent_name"]

		AGENT_ENDPOINT = settings["urls"]["get_agent"] + agent_name + "/"

		docker = subprocess.Popen("docker run -d ubuntu/ciberonline " \
									  "bash -c 'curl " \
									  "%s" \
									  " | tar -xz;" \
									  " py.test tests.py'" %  \
									  (AGENT_ENDPOINT, ),
									  shell = True, stdout = subprocess.PIPE)
		docker_container = docker.stdout.readline().strip()
		docker.wait()
		#print docker.returncode

		return AGENT_ENDPOINT

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
