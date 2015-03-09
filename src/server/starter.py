#encoding=utf-8
import subprocess
import tempfile
import requests
import socket
import time
import json
import os

def main():
	viewer_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	viewer_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	HOST = "http://127.0.0.1:8000"
	result = requests.get(HOST + "/api/v1/competitions/get_simulations/")
	simJson = json.loads(result.text)[0]
	tempFilesList = {}
	for key in simJson:
		if key == "agents" or key == "simulation_id":
			continue
			#Handle agents and simulation id
		fp = tempfile.NamedTemporaryFile()
		r = requests.get(HOST + simJson[key])
		fp.write(r.text)
		fp.seek(0)
		tempFilesList[key] = fp



	print "Process ID: ", os.getpid()
	print "Creating process for simulator.."
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

	print "Creating process for viewer.."
	viewer = subprocess.Popen(["python", "viewer.py"], stdout=subprocess.PIPE)
	print "Successfully opened process with process id: ", viewer.pid

	viewer_tcp.bind(("127.0.0.1", 7000))
	viewer_tcp.listen(1)
	viewer_c, viewer_c_addr = viewer_tcp.accept()

	print "Viewer ready.."

	n_agents = 5
	print "Sending message telling viewer how many agents there are..."
	viewer_c.send('<Robots Amount="'+str(n_agents)+'" />')
	for i in range(1, n_agents+1, 1):
		print "Opening Agent - " + str(i)
		agent = subprocess.Popen(["python", "./cibertools-v2.2/robsample/robsample_python.py", "-pos", str(i)], stdout=subprocess.PIPE)

		# print "Creating docker for agent.."
		# docker = subprocess.Popen(["docker", "run", "-d", "-P","ubuntu/ciberonline",\
		# 						"python", "./cibertools-v2.2/robsample/robsample_python.py",\
		# 						"--pos", str(i), "--host", "172.17.42.1"], stdout=subprocess.PIPE)
		# docker_container = docker.stdout.readline().strip()
		# docker.wait()
		# print "Successfully opened container: ", docker_container

		print "Successfully opened agent " + str(i) + " with process id: ", agent.pid

	data = viewer_c.recv(4096)
	while data != "<AllRobotsRegistered/>":
		data = viewer_c.recv(4096)
		print data

	print "Sending message to Viewer (everything is ready to start)"
	viewer_c.send("<StartedAgents/>")
	print "Waiting for simulation to end.."
	data = viewer_c.recv(4096)
	while data != "<EndedSimulation/>":
		data = viewer_c.recv(4096)
	print "Simulation ended, killing simulator and running agents"
	viewer_c.close()
	viewer_tcp.close()

	viewer.wait()
	# proc = subprocess.Popen(["docker", "stop", "-t", "0", docker_container])
	# proc.wait()
	# proc = subprocess.Popen(["docker", "rm", docker_container])
	# proc.wait()

	simulator.terminate()
	simulator.wait()

	for key in tempFilesList:
		tempFilesList[key].close()

if __name__ == "__main__":
    main()
