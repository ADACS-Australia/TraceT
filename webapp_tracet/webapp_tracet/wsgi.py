"""
WSGI config for webapp_tracet project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp_tracet.settings")

application = get_wsgi_application()

# Create a startup signal
from trigger_app.signals import startup_signal

# Send off start up signal because server is launching in production
startup_signal.send(sender=startup_signal)
