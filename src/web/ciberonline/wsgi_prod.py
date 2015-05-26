"""
WSGI config for ciberonline project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

print os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ciberonline.settings")

os.environ['DJANGO_SETTINGS_MODULE'] = 'ciberonline.settings'
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()