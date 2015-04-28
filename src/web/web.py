from threading import Thread

from dragon import *
from manage import *

if __name__ == "__main__":
    dragon = Dragon()
    dragon_thread = Thread(target=dragon.run, args=("0.0.0.0:9999",))
    dragon_thread.daemon = True
    dragon_thread.start()

    manage = Manage()
    manage_thread = Thread(target=manage.run, args=("0.0.0.0:8000",))
    manage_thread.daemon = True
    manage_thread.start()

    dragon_thread.join()
    manage_thread.join()