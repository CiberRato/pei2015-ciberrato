if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

echo "	>> Installing general dependencies"
apt-get install -y	python \
			build-essential \
			g++ \
			qt4-dev-tools \
			python-pip \
			python-cherrypy
			python-virtualenv \
			docker.io
(cd src/web;
echo "	>> Installing python dependencies"
pip install -r requirements.txt;

echo "	>> Migrating Django applications"
python manage.py migrate;)

echo "	>> Compiling cibertools"
(cd src/server/cibertools-v2.2/;
make;)
echo "	>> Creating docker image based on Dockerfile"
groupadd docker
gpasswd -a $USER docker

if [ $(lsb_release -a | grep "Ubuntu 14.04" | wc -l) != "0" ];
then
	service docker.io restart
	(cd src/server/;
	docker.io build -t ubuntu/ciberonline .)
else
	service docker restart
	(cd src/server/;
	docker build -t ubuntu/ciberonline .)
fi
echo "	Please logout and login again"
