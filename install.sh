if [ $(id -u) != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [ "$1" = "--help" ]; then
	echo "Please use this script under a Debian distribution"
	echo ""
	echo "Usage: ./install.sh [argument]"
	echo "Arguments:"
	echo "	--help - Shows this message"
	echo "	--env  - Use virtual environment for web"
	exit
fi

if [ "$1" = "--env" ]; then
	ENV=true
fi

echo "	>> Installing general dependencies"
apt-get install -y	python \
			build-essential \
			g++ \
			qt4-dev-tools \
			python-pip \
			python-virtualenv \
			docker.io
(cd src/web; 
if [ "$ENV" ]; then
echo "	>> Configuring virtual environment"
	if [ ! -d "environment" ]; then
		virtualenv environment
	fi
source environment/bin/activate;
fi
echo "	>> Installing python dependencies"
pip install -r requirements.txt;
echo "	>> Migrating Django applications"
python manage.py migrate;
if [ "$ENV" ]; then
	deactivate
fi)
echo "	>> Compiling cibertools"
(cd src/server/cibertools-v2.2/;
make --quiet;)
echo "	>> Creating docker image based on Dockerfile"
groupadd docker
gpasswd -a ${USERNAME} docker
#(cd src/server/;
#docker build -t ubuntu/ciberonline;)
