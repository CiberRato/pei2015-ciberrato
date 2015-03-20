import requests
import re
import json

def main():
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)
	HOST = settings["urls"]["post_sim_id"]

	params = {'simulation_identifier': "0a256950-7a5c-403d-aba3-52e455d197c5" }
	result = requests.post(HOST, params)
	print result.text


if __name__ == "__main__":
	main()
