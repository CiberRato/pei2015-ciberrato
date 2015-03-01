# Obtaining IP from interface
# ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2
#
# sudo build -t ubuntu/ciberonline .
# sudo docker run ubuntu/ciberonline python robsample_python.py --host $(ifconfig docker0 | grep "inet addr" | tr -s " " | sed -e 's/^[ \t]*//' | cut -f 2 -d " " | cut -d ":" -f 2)
#

FROM ubuntu
EXPOSE 6000
RUN apt-get update && apt-get install -y \
	python
RUN mkdir /code
WORKDIR /code
ADD ./cibertools-v2.2/robsample/ /code/