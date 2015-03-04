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

	HOST = "http://127.0.0.1:8000/"
	result = requests.get(HOST + "api/v1/get_simulation/")
	simJson = json.loads(result.text)[0]
	tempFilesList = {}
	for key in simJson:
		fp = tempfile.NamedTemporaryFile()
		fp.write(requests.get(HOST + simJson[key]).text)
		fp.seek(0)
		tempFilesList[key] = fp

	print "Process ID: ", os.getpid()
	print "Creating process for simulator.."
	##		CHECK ./simulator --help 				##
	# Run simulator for LINUX
	# simulator = subprocess.Popen(["./cibertools-v2.2/simulator/simulator", \
	#  				"-param", 	tempFilesList["param_list_path"].name, \
	#  				"-lab", 	tempFilesList["lab_path"].name, \
	#  				"-grid", 	tempFilesList["grid_path"].name], \
	#  				stdout = subprocess.PIPE)


	#run simulator for MAC_OSX
	simulator = subprocess.Popen(["../../../cibertools_OSX/simulator-adapted/simulator",\
					"-param", 	tempFilesList["param_list_path"].name,\
					"-lab",	 	tempFilesList["lab_path"].name,\
					"-grid", 	tempFilesList["grid_path"].name],\
					stdout=subprocess.PIPE)

	print "Successfully opened process with process id: ", simulator.pid
	time.sleep(1)

	print "Creating process for viewer.."
	viewer = subprocess.Popen(["python", "viewer.py"], stdout=subprocess.PIPE)
	print "Successfully opened process with process id: ", viewer.pid

	viewer_tcp.bind(("127.0.0.1", 7000))
	viewer_tcp.listen(1)
	viewer_c, viewer_c_addr = viewer_tcp.accept()

	print "Viewer ready.."

	# print "Creating docker for agent.."
	# docker = subprocess.Popen(["docker", "run", "-H", "tcp://192.168.59.103:2376",\
	# 							"python", "robsample_python.py",\
	# 							"--host", "172.17.42.1",\
	# 							"--pos", "1"], stdout=subprocess.PIPE)
	# docker_container = docker.stdout.readline().strip()
	# docker.wait()

	# print "Successfully opened container: ", docker_container
	# time.sleep(1)

	n_agents = 5
	print "Sending message telling viewer how many agents there are..."
	viewer_c.send('<Robots Amount="'+str(n_agents)+'" />')
	for i in range(1, n_agents+1, 1):
		print "Opening Agent - " + str(i)
		agent = subprocess.Popen(["python", "./cibertools-v2.2/robsample/robsample_python.py", "--pos", str(i)], stdout=subprocess.PIPE)
		print "Successfully opened agent " + str(i) + " with process id: ", agent.pid

	print "Sending message to Viewer (everything is ready to start)"
	viewer_c.send("<StartedAgents/>")
	print "Waiting for simulation to end.."
	data = viewer_c.recv(4096)
	while data != "<EndedSimulation/>":
		data = viewer_c.recv(4096)
	print "Simulation ended, killing simulator and running agents"
	viewer_c.close()

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
