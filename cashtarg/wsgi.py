

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cashtarg.settings.staging")

application = get_wsgi_application()
