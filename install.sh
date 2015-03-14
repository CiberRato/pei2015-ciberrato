if [ "$1" == "--help" ]; then
	echo "Please use this script under a Debian distribution"
	echo ""
	echo "Usage: ./install.sh [argument]"
	echo "Arguments:"
	echo "	--help - Shows this message"
	echo "	--env  - Use virtual environment for web"
	exit
fi
if [ "$1" == "--env" ]; then
	ENV=true
fi
echo "	>> Installing general dependencies"
sudo apt-get install -y	python \
			build-essential \
			g++ \
			qt4-dev-tools \
			python-pip \
			python-virtualenv

(cd src/web; 
if [ "$ENV" ]; then
echo "	>> Configuring virtual environment"
	if [ ! -d "environment" ]; then
		virtualenv environment
	fi
source environment/bin/activate;
fi
echo "	>> Installing python dependencies"
pip install 	Django==1.7.4 \
		dj-database-url==0.3.0 \
		dj-static==0.0.6 \
		django-appconf==0.6 \
		django-compressor==1.4 \
		djangorestframework==3.0.0 \
		drf-nested-routers==0.9.0 \
		gunicorn==19.1.1 \
		six==1.8.0 \
		static3==0.5.1 \
		wsgiref==0.1.2;
python manage.py migrate;
if [ "$ENV" ]; then
	deactivate
fi)
echo "	>> Compiling cibertools"
(cd src/server/cibertools-v2.2/;
make;)
