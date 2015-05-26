#encoding=utf-8
import subprocess
import netifaces
import tempfile
import requests
import socket
import time
import json
import os
import gzip
import sys
import tarfile
import re
import zipfile
import bz2
import multiprocessing
from threading import Thread
from xml.dom import minidom
from viewer import *


class Starter:
	def main(self,sim_id, simulator_port, running_ports, semaphore):
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		DJANGO_HOST = settings["settings"]["django_host"]
		DJANGO_PORT = settings["settings"]["django_port"]

		URL = settings["urls"]["error_msg"]

		try:
			self.run(sim_id, simulator_port)
		except Exception as e:
			print "[STARTER] Sending error message: " + e.args[0]
			data = {'trial_identifier': sim_id,'msg': e.args[0]}
			response = requests.post("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + URL, data=data)
			if response.status_code != 201:
				print "[STARTER] ERROR: Posting error to end point"

		for i in range(0,len(running_ports[:])):
			if running_ports[i] == simulator_port:
				running_ports[i] = 0
				print running_ports[:]
				break
		semaphore.release()

	def run(self,sim_id, simulator_port):
		# Find docker ip
		DOCKERIP = None
		for interface in netifaces.interfaces():
			if interface.startswith('docker'):
				DOCKERIP = netifaces.ifaddresses(interface)[2][0]['addr']
				break
		if DOCKERIP == None:
			raise Exception("[STARTER] ERROR: Please check your docker interface")
		else:
			print "[STARTER] Docker interface: %s" % (DOCKERIP, )

		# Loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		GET_SIM_URL = settings["urls"]["get_simulation"]

		POST_SIM_URL = settings["urls"]["post_log"]

		DJANGO_HOST = settings["settings"]["django_host"]
		DJANGO_PORT = settings["settings"]["django_port"]

		SERVICES_HOST = settings["settings"]["services_end_point_host"]
		SERVICES_PORT = settings["settings"]["services_end_point_port"]

		LOG_FILE = settings["settings"]["log_info_file"]
		LOG_FILE += str(simulator_port)

		SYNC_TIMEOUT = settings["settings"]["sync_timeout"]
		# End loading settings
		# Get simulation
		url = "http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + GET_SIM_URL + sim_id + "/"
		result = requests.get(url)
		if result.status_code != 200:
			raise Exception("[STARTER] ERROR: Simulation failed to load data")

		print result.text
		hall_of_fame = False
		simJson = json.loads(result.text)
		tempFilesList = {}
		n_agents = 0
		for key in simJson:
			#Handle agents and simulation id
			if key == "agents":
				n_agents = len(simJson[key])
				agents = simJson[key]
				if n_agents == 0:
					raise Exception("[STARTER] ERROR: Simulation has no agents")
				continue
			if key == "trial_id":
				if sim_id != simJson[key]:
					raise Exception("[STARTER] ERROR: sim_id received not the the same as the one in the simulation")
				continue
			if key == "type_of_competition":
				details = simJson[key]
				TIMEOUT = details["timeout"] * 60
				if TIMEOUT < 1:
					raise Exception("[STARTER] ERROR: Timeout invalid")
				allow_remote = details["allow_remote_agents"]
				if not isinstance(allow_remote, bool):
					raise Exception("[STARTER] ERROR: Allow Remote Field invalid")
				sync = details["synchronous_simulation"]
				if not isinstance(sync, bool):
					raise Exception("[STARTER] ERROR: Synchronous Simulation Field invalid")
				hof = details["name"]
				if hof == "Hall of fame - Single":
					hall_of_fame = True
				continue

			fp = tempfile.NamedTemporaryFile()
			r = requests.get("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + simJson[key])
			if r.status_code != 200:
				raise Exception("[STARTER] ERROR: Error getting " + key + " file from end-point")
			fp.write(r.text)
			fp.seek(0)
			tempFilesList[key] = fp


		print "[STARTER] Process ID: ", os.getpid()

		##CHECK ./simulator --help 				##
		# Run simulator for LINUX
		if sync:
			print "[STARTER] Creating process for simulator in sync mode on port " + str(simulator_port)
			simulator = subprocess.Popen(["./cibertools-v2.2/simulator/simulator", \
						"-nogui", \
						"-port",	str(simulator_port), \
						"-sync",	str(SYNC_TIMEOUT), \
						"-param", 	tempFilesList["param_list"].name, \
						"-lab", 	tempFilesList["lab"].name, \
						"-grid", 	tempFilesList["grid"].name], \
						stdout = subprocess.PIPE)
		else:
			print "[STARTER] Creating process for simulator"
			simulator = subprocess.Popen(["./cibertools-v2.2/simulator/simulator", \
						"-nogui", \
						"-port",	str(simulator_port), \
						"-param", 	tempFilesList["param_list"].name, \
						"-lab", 	tempFilesList["lab"].name, \
						"-grid", 	tempFilesList["grid"].name], \
						stdout = subprocess.PIPE)

		print "[STARTER] Successfully opened process with process id: ", simulator.pid
		time.sleep(1)

		print "[STARTER] Creating process for viewer"
		viewer_c, starter_c = multiprocessing.Pipe(True)
		timeout_event = multiprocessing.Event()
		viewer = Viewer()
		viewer_thread = multiprocessing.Process(target=viewer.main, args=(sim_id, allow_remote, sync, starter_c,timeout_event,simulator_port, hall_of_fame))
		viewer_thread.start()
		starter_c.close()
		print "[STARTER] Successfully opened viewer"

		print "[STARTER] Viewer ready, sending message to viewer about the number of agents"
		data = '<Robots Amount="' +str(n_agents)+'" />'
		viewer_c.send(data)

		# Launching agents
		docker_containers = []
		for i in range(n_agents):
			if agents[i]['agent_type'] == "local":
				print "[STARTER] Creating docker for agent: \n\tName: %s\n\tPosition: %s\n\tLanguage: %s" % \
						(agents[i]['agent_name'], agents[i]['pos'], agents[i]['language'], )

				docker = subprocess.Popen("docker run -d ubuntu/ciberonline " \
										  "bash -c 'curl " \
										  "http://%s:8000%s" \
										  " | tar -xz;"
										  " chmod +x prepare.sh execute.sh; ./prepare.sh; ./execute.sh %s %s %s'" %  \
										  (DOCKERIP, agents[i]['files'], DOCKERIP+":"+str(simulator_port),
										  agents[i]['pos'], agents[i]['agent_name'], ),
										  shell = True, stdout = subprocess.PIPE)
				docker_container = docker.stdout.readline().strip()
				docker_containers += [  ]
				docker.wait()
				print "[STARTER] Successfully opened container: %s" % (docker_container, )

		# Waiting for viewer to send robots registry confirmation
		# Use events to create timeouts
		timeout_event.wait(TIMEOUT)

		if not timeout_event.is_set():
			print "[STARTER] Failed to register all robots in the timeout established. Port: " + str(simulator_port)
			# Canceling everything regarding this simulation
			# Shuting down connections to viewer
			print "[STARTER] Killing Sockets"
			viewer_c.close()

			# Waiting for viewer to die
			print "[STARTER] Killing Viewer"
			viewer_thread.terminate()
			viewer_thread.join()

			# Kill simulator
			print "[STARTER] Killing Simulator"
			simulator.terminate()
			simulator.wait()

			if not sync:
				# Killing Websockets
				print "[STARTER] Killing Websocket"
				websocket.terminate()
				websocket.wait()

			# Kill docker container
			print "[STARTER] Killing Docker Containers"
			for dock in docker_containers:
				proc = subprocess.Popen(["docker", "stop", "-t", "0", dock])
				proc.wait()
				proc = subprocess.Popen(["docker", "rm", dock])
				proc.wait()

			# Remove log file from system
			print "[STARTER] Removing log file"
			os.remove(LOG_FILE)

			# Close all tmp files
			print "[STARTER] Closing tmp files"
			for key in tempFilesList:
				tempFilesList[key].close()
			raise Exception("[STARTER] ERROR: Agents weren't all registered")

		timeout_event.clear()
		# Stuff for start
		if allow_remote:
			services_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			services_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			services_tcp.bind((SERVICES_HOST, SERVICES_PORT))
			services_tcp.listen(1)
			print "[STARTER] Waiting for start.."
			services_c, services_c_addr = services_tcp.accept()

			data = None
			data = services_c.recv(1024)
			data = data.split("=")
			while data[0] != "start":
				data = services_c.recv(1024)
				data = data.split("=")

			if data[1] != sim_id:
				print "[STARTER] Start received not the same as the current trial. Port: " + str(simulator_port)
				# Canceling everything regarding this simulation
				# Shuting down connections to viewer
				print "[STARTER] Killing Sockets"
				viewer_c.close()

				services_c.shutdown(socket.SHUT_RDWR)
				services_c.close()
				services_tcp.shutdown(socket.SHUT_RDWR)
				services_tcp.close()

				# Waiting for viewer to die
				print "[STARTER] Killing Viewer"
				viewer_thread.terminate()
				viewer_thread.join()

				# Kill simulator
				print "[STARTER] Killing Simulator"
				simulator.terminate()
				simulator.wait()

				if not sync:
					# Killing Websockets
					print "[STARTER] Killing Websocket"
					websocket.terminate()
					websocket.wait()

				# Kill docker container
				print "[STARTER] Killing Docker Containers"
				for dock in docker_containers:
					proc = subprocess.Popen(["docker", "stop", "-t", "0", dock])
					proc.wait()
					proc = subprocess.Popen(["docker", "rm", dock])
					proc.wait()

				# Remove log file from system
				print "[STARTER] Removing log file"
				os.remove(LOG_FILE)

				# Close all tmp files
				print "[STARTER] Closing tmp files"
				for key in tempFilesList:
					tempFilesList[key].close()
				raise Exception("[STARTER] Start received not the same as the current trial")

		else:
			time.sleep(0.1)
		print "[STARTER] Sending message to Viewer (everything is ready to start)"
		viewer_c.send("<StartedAgents/>")

		print "[STARTER] Waiting for simulation to end.."
		data = viewer_c.recv()
		while data != "<EndedSimulation/>":
			data = viewer_c.recv()

		print "[STARTER] Simulation ended, killing simulator and running agents, port: " + str(simulator_port)

		# Shuting down connections to viewer
		viewer_c.close()

		if allow_remote:
			services_c.shutdown(socket.SHUT_RDWR)
			services_c.close()
			services_tcp.shutdown(socket.SHUT_RDWR)
			services_tcp.close()

		# Waiting for viewer to die
		viewer_thread.join()

		# Kill docker container
		for dock in docker_containers:
			proc = subprocess.Popen(["docker", "stop", "-t", "0", dock])
			proc.wait()
			proc = subprocess.Popen(["docker", "rm", dock])
			proc.wait()

		# Kill simulator
		simulator.terminate()
		simulator.wait()

		print "[STARTER] Posting log to the database.. Port: " + str(simulator_port)
		# save file with name = trial.identifier + '.json.bz2' em bz
		temp = tempfile.NamedTemporaryFile(delete=True)
		temp.name = sim_id + '.json.bz2'
		output = open(temp.name, "wb")
		output.write(bz2.compress(open(LOG_FILE, "r").read()))
		output.close()
		# Save log to the end-point
		data = {'trial_identifier': sim_id}
		files = {'log_json': open(temp.name, "r").read()}
		response = requests.post("http://" + DJANGO_HOST + ':' + str(DJANGO_PORT) + POST_SIM_URL, data=data, files=files)
		temp.close()

		if response.status_code != 201:
			raise Exception("[STARTER] ERROR: error posting log file to end point")

		print "[STARTER] Log successfully posted, starter closing now.. Port: " + str(simulator_port)

		# Remove log file from system
		os.remove(LOG_FILE)

		# Close all tmp files
		for key in tempFilesList:
			tempFilesList[key].close()

		print "[STARTER] Simulation " + sim_id + " on port " + str(simulator_port) + " finished successfully..\n"
		return

if __name__ == "__main__":
	main()
