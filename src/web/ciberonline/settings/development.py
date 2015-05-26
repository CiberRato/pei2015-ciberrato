from base import *


# debug options
DEBUG = True
TEMPLATE_DEBUG = True

# password recover URLs
CHECK_EMAIL_URL = "http://localhost:8000/check/email/"
PASSWORD_RECOVER_EMAIL_URL = "http://localhost:8000/idp/recover/"

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# local endpoints to fire simulations
START_SIM_ENDPOINT = "http://127.0.0.1:9000/api/v1/trials/start/"
PREPARE_SIM_ENDPOINT = "http://127.0.0.1:9000/api/v1/trial_id/"

TEST_CODE_ENDPOINT = "http://127.0.0.1:9000/api/v1/test_agent/?agent_name=<agent_name>&team_name=<team_name>/"

# swampdragon settings
DRAGON_URL = 'http://localhost:9999/'
