#encoding=utf-8
import subprocess
import socket
import time
import os

def main():
	print "Process ID: ", os.getpid()
	print "Opening process for simulator"
	simulator = subprocess.Popen("./iia-myrob/cibertools/simulator-adapted/simulator", shell=False, stdout=subprocess.PIPE)
	time.sleep(1)

	print "Opening process for viewer"
	viewer = subprocess.Popen("python viewer.py", shell=True, stdout=subprocess.PIPE)
	time.sleep(1)

	viewer_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	viewer_c.connect(("127.0.0.1", 7000))

	print "Opening process for agent"
	agent = subprocess.Popen("python iia-myrob/cibertools/myrob.py", shell=True, stdout=subprocess.PIPE)
	time.sleep(1)

	print "Sends a message to Viewer telling that agents are ready"
	viewer_c.send("<StartedAgents/>")
	print viewer_c.recv(4096)
	print "Simulation ended, killing simulator and running agents"
	viewer_c.close()

	agent.terminate()
	simulator.terminate()

if __name__ == "__main__":
    main()