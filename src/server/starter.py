#encoding=utf-8
import subprocess
import netifaces
import tempfile
import requests
import socket
import time
import json
import os
import sys
import tarfile
import re
import zipfile
from xml.dom import minidom

class Starter:

	def main(self):
		#loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		END_POINT_HOST = settings["settings"]["starter_end_point_host"]
		END_POINT_PORT = settings["settings"]["starter_end_point_port"]

		print "Starter is in deamon mode, waiting for simulation.."
		end_point_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		end_point_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		end_point_tcp.bind((END_POINT_HOST, END_POINT_PORT))
		end_point_tcp.listen(1)
		end_point_c, end_point_add = end_point_tcp.accept()

		data = None
		while 1:
			while data == None:
				data = end_point_c.recv(1024)
			print "Received simulation with sim_id= " + data + ", starting now.."
			self.run(data)
			data = None

	def run(self,sim_id):
		DOCKERIP = None
		for interface in netifaces.interfaces():
			if interface.startswith('docker'):
				DOCKERIP = netifaces.ifaddresses(interface)[2][0]['addr']
				break
		if DOCKERIP == None:
			print "Please check your docker interface."
			exit(-1)
		else:
			print "Docker interface: %s" % (DOCKERIP, )

		#loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		TIMEOUT = settings["settings"]["timeout"]

		GET_SIM_HOST = settings["urls"]["get_simulation"]

		POST_SIM_HOST = settings["urls"]["post_log"]

		VIEWER_HOST = settings["settings"]["starter_viewer_host"]
		VIEWER_PORT = settings["settings"]["starter_viewer_port"]

		LOG_FILE = settings["settings"]["log_info_file"]
		PARAM_FILE = settings["settings"]["params_file"]
		LAB_FILE = settings["settings"]["lab_file"]
		GRID_FILE = settings["settings"]["grid_file"]

		TAR_FILE = settings["settings"]["file"]
		#end loading settings

		print GET_SIM_HOST + sim_id + "/"
		result = requests.get(GET_SIM_HOST + sim_id + "/")
		print result.text
		simJson = json.loads(result.text)
		tempFilesList = {}
		n_agents = 0
		host = GET_SIM_HOST.split("/api")[0]

		for key in simJson:
			#Handle agents and simulation id
			if key == "agents":
				n_agents = len(simJson[key])
				agents = simJson[key]
				continue
			if key == "simulation_id":
				if sim_id != simJson[key]:
					print "ERROR: sim_id received not the the same in the simulation"
					return
				continue

			fp = tempfile.NamedTemporaryFile()
			r = requests.get(host + simJson[key])
			fp.write(r.text)
			fp.seek(0)
			tempFilesList[key] = fp

		print "Number of agents to be loaded: " + str(n_agents)

		print "Process ID: ", os.getpid()

		print "Creating process for Websocket end-point.."
		websocket = subprocess.Popen(["python", "./websockets/monitor.py"], stdout=subprocess.PIPE)
		print "Successfully opened process with process id: ", websocket.pid
		time.sleep(1)
		print "Creating process for simulator"
		##		CHECK ./simulator --help 				##
		# Run simulator for LINUX
		simulator = subprocess.Popen(["./cibertools-v2.2/simulator/simulator", \
						"-nogui", \
						"-param", 	tempFilesList["param_list"].name, \
						"-lab", 	tempFilesList["lab"].name, \
						"-grid", 	tempFilesList["grid"].name], \
						stdout = subprocess.PIPE)

		print "Successfully opened process with process id: ", simulator.pid
		time.sleep(1)
		print "Creating process for viewer"
		viewer = subprocess.Popen(["python", "viewer.py"])
		print "Successfully opened process with process id: ", viewer.pid

		viewer_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		viewer_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		viewer_tcp.bind((VIEWER_HOST, VIEWER_PORT))
		viewer_tcp.listen(1)
		viewer_c, viewer_c_addr = viewer_tcp.accept()

		print "Viewer ready, sending message to viewer about the number of agents\n"
		viewer_c.send('<Robots Amount="' +str(n_agents)+'" />')

		remote = False
		for i in range(n_agents):
			if agents[i]['agent_type'] == "local":
				print "Creating docker for agent: \n\tName: %s\n\tPosition: %s\n\tLanguage: %s" % \
						(agents[i]['agent_name'], agents[i]['pos'], agents[i]['language'], )
				docker = subprocess.Popen("docker run -d ubuntu/ciberonline " \
										  "bash -c 'curl " \
										  "http://%s:8000%s" \
										  " | tar -xz;" \
										  " python myrob.py -host %s -pos %s'" %  \
										  (DOCKERIP, agents[i]['files'], DOCKERIP, agents[i]['pos'], ),
										  shell = True, stdout = subprocess.PIPE)
				docker_container = docker.stdout.readline().strip()
				docker.wait()
				print "Successfully opened container: %s\n" % (docker_container, )
			else:
				remote = True

		if remote:
			print "Remote agents may start registering"
			sleep(TIMEOUT) #timeout for people to register their robots
			print "Remote agents timeout reached, simulation will start now.."


		data = viewer_c.recv(4096)
		while data != "<AllRobotsRegistered/>":
			data = viewer_c.recv(4096)

		print "Sending message to Viewer (everything is ready to start)"
		viewer_c.send("<StartedAgents/>")
		print "Waiting for simulation to end.."
		data = viewer_c.recv(4096)
		while not data.find("EndedSimulation"):
			data = viewer_c.recv(4096)
		print "Simulation ended, killing simulator and running agents"
		print "Posting log to the database.."

		viewer_c.shutdown(socket.SHUT_RDWR)
		viewer_c.close()
		viewer_tcp.shutdown(socket.SHUT_RDWR)
		viewer_tcp.close()

		viewer.wait()

		proc = subprocess.Popen(["docker", "stop", "-t", "0", docker_container])
		proc.wait()
		proc = subprocess.Popen(["docker", "rm", docker_container])
		proc.wait()

		simulator.terminate()
		simulator.wait()


		#compressing json file to tar.gz
		# TAR_FILE = TAR_FILE.replace("<SIM_ID>", sim_id)
		# json_gz = zipfile.ZipFile(TAR_FILE, mode='a')
		# json_gz.write(LOG_FILE, arcname=LOG_FILE)
		# json_gz.write(PARAM_FILE, arcname=PARAM_FILE)
		# json_gz.write(LAB_FILE, arcname=LAB_FILE)
		# json_gz.write(GRID_FILE, arcname=GRID_FILE)
		#json_gz.write("tmp.json", arcname="tmp.json")

		# json_gz.close()

		#save log to the end-point
		data = {'simulation_identifier': sim_id}
		#files = {'log_json': open(TAR_FILE, "rb")}
		files = {'log_json': open(LOG_FILE, "r")}
		response = requests.post(POST_SIM_HOST, data=data, files=files)

		#print response.status_code
		#print response.text
		if response.status_code != 201:
			print "ERROR: error posting log file to end point"
			return


		print "Log successfully posted, starter closing now.."

		os.remove(LOG_FILE)
		os.remove(PARAM_FILE)
		os.remove(LAB_FILE)
		os.remove(GRID_FILE)
		#os.remove(TAR_FILE)

		for key in tempFilesList:
			tempFilesList[key].close()

		print "Simulation " + sim_id + " finished successfully.."


if __name__ == "__main__":
	main()
