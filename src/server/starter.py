#encoding=utf-8
import subprocess
import socket
import time
import os

def main():
	print "Process ID: ", os.getpid()
	print "Opening process for simulator"
	simulator = subprocess.Popen("./iia-myrob/cibertools/simulator-adapted/simulator", stdout=subprocess.PIPE)
	time.sleep(1)

	print "Opening process for viewer"
	viewer = subprocess.Popen("python viewer.py", shell=True, stdout=subprocess.PIPE)
	time.sleep(1)


	viewer_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	viewer_c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	viewer_c.connect(("127.0.0.1", 7000))

	print "Opening process for agent"
	agent = subprocess.Popen("python iia-myrob/cibertools/myrob.py", shell=True, stdout=subprocess.PIPE)
	time.sleep(1)

	print "Sends a message to Viewer telling that agents are ready"
	viewer_c.send("<StartedAgents/>")
	data = viewer_c.recv(4096)
	while data != "<EndedSimulation/>":
		data = viewer_c.recv(4096)
	print "Simulation ended, killing simulator and running agents"
	viewer_c.close()
	#print "Viewer ID: ", viewer.pid()
	#print "Sim ID: ", simulator.pid()
	#print "Agent ID: ", agent.pid()

	viewer.wait()
	#agent.terminate()
	#agent.kill()
	agent.wait()
	simulator.terminate()

if __name__ == "__main__":
    main()