if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

#set -e -o
user=$(who am i | awk '{print $1}')
echo "	>> Installing general dependencies"
apt-get update && apt-get install -y	python \
			build-essential \
			g++ \
			qt4-dev-tools \
			python-pip \
			python-dev \
			python-virtualenv \
			docker.io \
			redis-server \
			libfreetype6-dev \
			libxft-dev  \
			libjpeg62 \
			libpq-dev
			
(cd src/web;
echo "	>> Installing python dependencies"
pip install cherrypy \
			netifaces \
			xmltodict \
			flufl.enum
pip install -r requirements.txt;

echo "	>> Migrating Django applications"
sudo -u $user python manage.py migrate;

echo "	>> Django Simple Captcha"
if ! python manage.py test captcha; then
	/usr/bin/yes | sudo pip uninstall pillow;
	pip install pillow;
fi)

# This should disappear from here after not needed
(cd src/server/;
sudo -u $user mkdir tmp;)

echo "	>> Compiling cibertools"
(cd src/server/cibertools-v2.2-AV2015/;
make;)
echo "	>> Creating docker image based on Dockerfile"
groupadd docker
gpasswd -a $user docker

if [ $(lsb_release -a | grep "Ubuntu 14.04" | wc -l) != "0" ];
then
	service docker.io restart
	sleep 2
	(cd src/server/;
	docker.io build -t ubuntu/ciberonline .)
else
	service docker restart
	sleep 2
	(cd src/server/;
	docker build -t ubuntu/ciberonline .)
fi
echo "	Please logout and login again"
