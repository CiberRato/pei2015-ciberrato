import subprocess


if __name__ == "__main__":
    dragon = subprocess.Popen(["python", "dragon.py", "0.0.0.0:8080"])
    stream = subprocess.Popen(["python", "manage.py", "stream"])

    dragon.wait()
    stream.kill()