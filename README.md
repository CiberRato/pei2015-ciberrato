Project Description: http://xcoa.av.it.pt/~pei2015-ciberonline/
Project Documentation: http://code.ua.pt/projects/pei2015-ciberonline/wiki

** HOW TO INSTALL? [Debian based system]**
	./install.sh [with adminstration rights]

** HOW TO RUN?
You need to run 2 python scripts at this moment.

First one will run the django server:
	cd src/web; python manage.py runserver 0.0.0.0:8000

Second one will run all services needed to simulate and communicate with Django:
	cd src/server; python start_services.py

At this point webpage will be available at http://localhost:8000/