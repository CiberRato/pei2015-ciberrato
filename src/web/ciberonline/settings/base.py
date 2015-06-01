"""
Django settings for ciberonline project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../../"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ggv8+_0p@b6t+y)3k6aul!qpj&73*#@hbw8o_4mdx)8-=jp^n$'


ALLOWED_HOSTS = []

# emails
ADMINS = (('Rafael', 'mail@rafaelferreira.pt'),)
"""
DEFAULT_FROM_EMAIL = "ciberrato@rafaelferreira.pt"
SERVER_EMAIL = "ciberrato@rafaelferreira.pt"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_HOST_PASSWORD = "ciberrato"
EMAIL_HOST_USER = "ciberrato@rafaelferreira.pt"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
"""

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'CIBER RATO <ciber@ciberrato.vm.atnog.av.it.pt>'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'swampdragon',
    'swampdragon_auth',
    'rest_framework',
    'authentication',
    'teams',
    'agent',
    'competition',
    'notifications',
    'tokens',
    'stickynote',
    'captcha',
    'statistics'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

ROOT_URLCONF = 'ciberonline.urls'

WSGI_APPLICATION = 'ciberonline.wsgi.application'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Lisbon'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

NUMBER_OF_NOTIFICATIONS_TO_SAVE = 5
MAX_PRIVATE_COMPETITION_LOGS_SAVED_PER_TEAM = 10

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ALLOWED_UPLOAD_LANGUAGES = (
    ('Python', 'Python'),
    ('C++', 'cplusplus'),
    ('Java', 'Java')
)
ALLOWED_UPLOAD_SIZE = 50000000  # bytes

PRIVATE_COMPETITIONS_NAME = "Private Competition"

HALL_OF_FAME_START_STR = "Hall of fame - "

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', False)

AUTH_USER_MODEL = 'authentication.Account'

ALLOWED_HOSTS = ['*.aws.atnog.av.it.pt', '*.atnog.org', '*']

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

# SwampDragon settings
SWAMP_DRAGON_CONNECTION = ('notifications.socketconnection.HttpDataConnection', '/data')

# Catpcha
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)