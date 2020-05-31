"""
WSGI config for blob_storage project.

It exposes the WSGI callable as a module-level variable named ``api``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blob_storage.settings")

application = get_wsgi_application()
