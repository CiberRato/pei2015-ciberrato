import requests
import re
import json

def main():
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)
	HOST = settings["urls"]["post_sim_id"]

	params = {'simulation_identifier': "50f5b704-65c5-4051-b5be-2555861812e7" }
	result = requests.post(HOST, params)
	print result.text
	print result.status_code


if __name__ == "__main__":
	main()
