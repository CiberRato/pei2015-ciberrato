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

class Test:
	def run(self, agent_name):
		# Find docker ip
		DOCKERIP = None
		for interface in netifaces.interfaces():
			if interface.startswith('docker'):
				DOCKERIP = netifaces.ifaddresses(interface)[2][0]['addr']
				break
		if DOCKERIP == None:
			print "Please check your docker interface."
			exit(-1)

		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		GET_AGENT_URL = settings["urls"]["get_agent"]

		AGENT_ENDPOINT = "http://" + DOCKERIP + ":8000" + GET_AGENT_URL + agent_name +"/"

		docker = subprocess.Popen("docker run ubuntu/ciberonline " \
									  "bash -c 'curl -s " \
									  "%s" \
									  " | tar -xz;" \
									  " python tests.py'" %  \
									  (AGENT_ENDPOINT, ),
									  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdout, stderr) = docker.communicate()
		if docker.returncode != 0:
			message = stderr
		else:
			message = "Passed tests with success"

		url = "http://localhost:8000/api/v1/agents/code_validation/"+agent_name+"/"
		data = {'code_valid': docker.returncode == 0, 'validation_result': message}
		requests.put(url, data=data)

if __name__ == "__main__":
	main()


