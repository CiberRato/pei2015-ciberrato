# Obtaining IP from interface
# ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2
#
# sudo build -t ubuntu/ciberonline .
# sudo docker run ubuntu/ciberonline python robsample_python.py --host $(ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2)
#

FROM ubuntu
EXPOSE 6000
RUN apt-get update
RUN apt-get install -y \
	python 
#	g++ 
#	..
#
RUN mkdir /code

# This going to get out of here after...
ADD ./cibertools-v2.2/robsample/ /code/

RUN groupadd -r lowrights && useradd -r -g lowrights agent
USER agent
WORKDIR /code