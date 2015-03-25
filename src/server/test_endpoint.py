import requests
import re
import json

def main():
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)
	HOST = settings["urls"]["post_sim_id"]

	params = {'simulation_identifier': "3349b88f-4268-48f8-b00b-ef3cc47b8956" }
	result = requests.post(HOST, params)
	print result.text
	print result.status_code


if __name__ == "__main__":
	main()
