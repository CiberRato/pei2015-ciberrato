from base import *


# debug options
DEBUG = False
TEMPLATE_DEBUG = False

# password recover URLs
CHECK_EMAIL_URL = "http://ciber.atnog.org/check/email/"
PASSWORD_RECOVER_EMAIL_URL = "http://ciber.atnog.org/idp/recover/"


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mydb',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'ciber_db',
        'PASSWORD': 'ciberonline',
        'HOST': 'localhost',
        # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

# local endpoints to fire simulations
START_SIM_ENDPOINT = "http://127.0.0.1:9000/api/v1/trials/start/"
PREPARE_SIM_ENDPOINT = "http://127.0.0.1:9000/api/v1/trial_id/"

TEST_CODE_ENDPOINT = "http://127.0.0.1:9000/api/v1/test_agent/?agent_name=<agent_name>&team_name=<team_name>/"

# swampdragon settings
DRAGON_URL = 'http://ciber.atnog.org:8080/'
