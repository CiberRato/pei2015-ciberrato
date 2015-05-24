import subprocess


if __name__ == "__main__":
    dragon = subprocess.Popen(["python", "dragon.py", "0.0.0.0:9999"])
    django = subprocess.Popen(["python", "manage.py", "runserver", "0.0.0.0:8000"])
    stream = subprocess.Popen(["python", "manage.py", "stream"])

    dragon.wait()
    django.wait()
    stream.kill()