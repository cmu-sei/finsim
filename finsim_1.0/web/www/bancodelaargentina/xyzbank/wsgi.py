"""
WSGI config for XYZ_Transaction_Server project.

"""
import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xyzbank.settings")

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))

application = get_wsgi_application()
