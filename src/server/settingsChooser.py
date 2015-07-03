import re
import json
from socket import gethostname

class Settings():
	def __init__(self):
		self.serverNames = ["ciber"]

	def getSettings(self):
		server_name = gethostname()
		for n in self.serverNames:
			if server_name == n:
				settings_str = re.sub("///.*", "", open("settings.json", "r").read())
				return json.loads(settings_str)

		settings_str = re.sub("///.*", "", open("settings-dev.json", "r").read())
		return json.loads(settings_str)
