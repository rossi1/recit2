import os

from .base import *


from decouple import config


STATICFILES_DIRS = (os.path.join('static'),)


DATABASES = {
   'default': {
       'ENGINE':'django.db.backends.postgresql',
       'NAME': 'juan',
       'USER': config('DB_USER'),
       'PASSWORD': config('DB_PASSWORD'),
       'HOST': '127.0.0.1',
       'PORT': ''
   }


}

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Lagos'

