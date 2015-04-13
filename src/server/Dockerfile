FROM ubuntu
EXPOSE 6000
EXPOSE 8000

RUN apt-get update && apt-get install -y curl wget \
	python default-jre default-jdk g++ build-essential qt4-qmake qt4-dev-tools \
	python-pip
RUN pip install pytest

RUN mkdir -p /ciber/user_sourcecode

# Adding python module to communicate with simulator
ADD ./libraries/python/ /ciber/
RUN mv /ciber/croblink.py $(python -c "from distutils.sysconfig import *; print(get_python_lib())")

# Adding c++ python libraries
ADD ./libraries/cpp /lib/

# Adding tests to the Docker
ADD ./compile_execute/tests.py /ciber/user_sourcecode/

WORKDIR /ciber/user_sourcecode
