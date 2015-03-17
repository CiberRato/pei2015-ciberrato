# Obtaining IP from interface
# ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2
#
# sudo build -t ubuntu/ciberonline .
# sudo docker run ubuntu/ciberonline python robsample_python.py --host $(ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2)
#

FROM ubuntu
EXPOSE 6000
EXPOSE 8000
RUN apt-get update
RUN apt-get install -y \
	curl \
	wget \
	python

RUN mkdir -p /ciber/user_sourcecode

# Adding python module to communicate with simulator
ADD ./libraries/python/ /ciber/
RUN mv /ciber/croblink.py $(python -c "from distutils.sysconfig import *; print(get_python_lib())")

#RUN groupadd -r lowrights && useradd -r -g lowrights agent
#USER agent
WORKDIR /ciber/user_sourcecode
