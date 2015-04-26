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
	def run(self, team_name, agent_name):
		# Find docker ip
		DOCKERIP = None
		for interface in netifaces.interfaces():
			if interface.startswith('docker'):
				DOCKERIP = netifaces.ifaddresses(interface)[2][0]['addr']
				break
		if DOCKERIP == None:
			print "Please check your docker interface."
			sys.exit(-1)

		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		GET_AGENT_URL = settings["urls"]["get_agent"]

		CODE_VALIDATION_URL = settings["urls"]["code_validation"]

		DJANGO_HOST = settings["settings"]["django_host"]
		DJANGO_PORT = settings["settings"]["django_port"]

		AGENT_ENDPOINT = "http://" + DOCKERIP + ":8000" + GET_AGENT_URL + team_name + "/" + agent_name +"/"

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

		url = "http://" + DJANGO_HOST + ":" + str(DJANGO_PORT) + CODE_VALIDATION_URL + agent_name + "/"
		data = {'team_name': team_name ,'code_valid': docker.returncode == 0, 'validation_result': message}
		requests.put(url, data=data)

		print "[TESTS] Test finished sucessfully"

if __name__ == "__main__":
	main()


