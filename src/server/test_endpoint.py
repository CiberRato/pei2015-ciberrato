import requests
import re
import json

def main():
	settings_str = re.sub("///.*", "", open("settings.json", "r").read())
	settings = json.loads(settings_str)
	HOST = "127.0.0.1:9000/api/v1/trials/start"

	params = {'trial_identifier': "9df02d7c-ac7d-4f38-903f-c2704eb37d38" }
	result = requests.post(HOST, params)
	print result.text
	print result.status_code


if __name__ == "__main__":
	main()
