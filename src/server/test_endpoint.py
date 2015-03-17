import requests


def main():
	sim_id = "0a256950-7a5c-403d-aba3-52e455d197c5"
	HOST = "http://127.0.0.1:9000"
	params = {'simulation_identifier': sim_id }
	result = requests.post(HOST + "/api/v1/simulation_id/", params)
	print result.text


if __name__ == "__main__":
	main()
