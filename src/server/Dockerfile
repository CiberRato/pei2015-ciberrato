FROM ubuntu
# Docker builds seems to have a bug related with chfn
RUN ln -s -f /bin/true /usr/bin/chfn

RUN apt-get update && apt-get install -y curl wget \
	python default-jre default-jdk g++ build-essential qt4-qmake qt4-dev-tools \
	python-pip zip unzip
RUN pip install pytest \
				flufl.enum

EXPOSE 6000
EXPOSE 6001
EXPOSE 6002
EXPOSE 6003
EXPOSE 6004
EXPOSE 6005
EXPOSE 6006
EXPOSE 6007
EXPOSE 6008
EXPOSE 8000
EXPOSE 80

RUN mkdir -p /ciber/user_sourcecode

# Adding python module to communicate with simulator
# Can't have 2 croblinks as default library
#ADD ./libraries/python/ /ciber/
#RUN mv /ciber/croblink.py $(python -c "from distutils.sysconfig import *; print(get_python_lib())")

# Adding croblink and CrobAv for Academia de Verao
ADD ./libraries/python_academia_verao/croblink.py /ciber/croblink.py
ADD ./libraries/python_academia_verao/CiberAV.py /ciber/CiberAV.py
RUN mv /ciber/croblink.py $(python -c "from distutils.sysconfig import *; print(get_python_lib())")
RUN mv /ciber/CiberAV.py $(python -c "from distutils.sysconfig import *; print(get_python_lib())")


# Adding c++ python libraries
ADD ./libraries/cpp /lib/

# Adding tests to the Docker
ADD ./compile_execute/tests.py /ciber/user_sourcecode/

WORKDIR /ciber/user_sourcecode
