#####Project Description: http://xcoa.av.it.pt/~pei2015-ciberonline/
#####Project Documentation: http://code.ua.pt/projects/pei2015-ciberonline/wiki

**How to install? [Debian based system]**
```sh 
./install.sh [with adminstration rights]
```

**How to run?**

You need to run 2 python scripts at this moment.
First one will run the django server:
```sh
	cd src/web; python manage.py runserver 0.0.0.0:8000
```
Second one will run all services needed to simulate and communicate with Django:
```sh
	cd src/server; python start_services.py
```

At this point webpage will be available at http://localhost:8000/