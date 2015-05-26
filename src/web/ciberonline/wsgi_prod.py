"""
WSGI config for ciberonline project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, '/home/ciber/pei2015-ciberonline/src/web/ciberonline')
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ciberonline.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
