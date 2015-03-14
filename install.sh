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
sudo apt-get install -y	python \
			build-essential \
			g++ \
			qt4-dev-tools \
			python-pip \
			python-virtualenv \
			docker.io
(cd src/web; 
if [ "$ENV" ]; 
then
	echo "	>> Configuring virtual environment"
	if [ ! -d "environment" ]; then
		virtualenv environment
	fi
	source environment/bin/activate;
	echo "	>> Installing python dependencies"
	pip install -r requirements.txt;
else
	echo "	>> Installing python dependencies"
	sudo pip install -r requirements.txt;
fi
echo "	>> Migrating Django applications"
python manage.py migrate;
if [ "$ENV" ]; then
	deactivate
fi)
echo "	>> Compiling cibertools"
(cd src/server/cibertools-v2.2/;
make;)
echo "	>> Creating docker image based on Dockerfile"
sudo groupadd docker
sudo gpasswd -a $USER docker
if [ $(lsb_release -a | grep "Ubuntu 14.04" | wc -l) != "0" ]; then
	sudo alias docker="docker.io"
fi
sudo service docker restart
(cd src/server/;
sudo docker build -t ubuntu/ciberonline .;)
echo "	Please logout and login again"
