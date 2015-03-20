import cherrypy
import socket
import re
import json

class GetSimId(object):

	def __init__(self):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)
		HOST = settings["settings"]["starter_end_point_host"]
		PORT = settings["settings"]["starter_end_point_port"]

		self.starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.starter_tcp.connect((HOST, PORT))

	@cherrypy.expose
	def index(self, **kwargs):

		sim_id = kwargs["simulation_identifier"]

		self.starter_tcp.send(str(sim_id))

		return "received sim id:" + str(sim_id)




if __name__ == '__main__':
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)
	HOST = settings["settings"]["end_point_host"]
	PORT = settings["settings"]["end_point_port"]


	cherrypy.config.update({'server.socket_host': HOST ,\
							'server.socket_port': PORT })
	cherrypy.quickstart(GetSimId(), "/api/v1/simulation_id/")
