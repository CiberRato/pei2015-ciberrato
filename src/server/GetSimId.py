import cherrypy
import subprocess
import socket


class GetSimId(object):

	def __init__(self):
		starter_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		starter_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	@cherrypy.expose
	def index(self, **kwargs):

		sim_id = kwargs["simulation_identifier"]
		# starter_tcp.connect(("127.0.0.1", 7500))

		# starter_tcp.send()

		return "received sim id:" + str(sim_id)




if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host': '127.0.0.1',\
							'server.socket_port': 9000 })
	cherrypy.quickstart(GetSimId(), "/api/v1/simulation_id/")
