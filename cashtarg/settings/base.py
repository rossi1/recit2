import os
from datetime import timedelta

from decouple import config
import dj_database_url
#import cloudinary.api



SECRET_KEY = config('SECRET_KEY')


ALLOWED_HOSTS = ['*']

DEBUG = config('DEBUG', cast=bool)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders'

]

LOCAL_APPS = [
      
    'accounts',
    'wallet',
    'invoice',
    'transaction',
    'subscription',
    'inventory_system'

]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cashtarg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cashtarg.wsgi.application'




# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 


AUTH_USER_MODEL = 'accounts.User'

MEDIA_ROOT = os.path.join(DIR, 'media')

MEDIA_URL = '/media/'



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',

    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
        
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}



CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)


STATIC_URL = '/static/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_PORT = 587

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_MINTUES = 60

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-token',
    'x-TOKEN',
    'x-Token',
    'x_token',
    'x_TOKEN',
    'x_Token',
    'x_token'
)


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=4),  # testing
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # testing
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('SECRET_KEY') #env("DJANGO_SECRET_KEY"),
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

ACCOUNT_SID = 'ACe16929531bae78596e50b0185a877442'
AUTH_TOKEN = '31fcedd10b248ef38f383c3cd98f7852'

EMAIL_ADMINS = [
    'emmanuelukwuegbu2016@gmail.com',
    'creative.joe007@gmail.com'
]


ONE_TIME  = 'one-time'
RECURRING_BILLING = 'recurring-billing'
RECURRING_WEEKLY = 'week'
RECURRING_MONTHLY = 'month'
RECURRING_DAILY = 'day'

AUTOMATED_REMINDERS_DAYS = { 
    'MONDAY': 0,
    'TUESDAY':1,
    'WEDNESDAY': 2,
    'THURSDAY':3,
    'FRIDAY': 4,
    'SATURDAY': 5,
    'SUNDAY': 6
}

AUTOMATED_REMINDER_TYPE = {
    'ONCE': 'ONCE', 
    'EVERYDAY': 'EVERYDAY'
}

LINK_URL = 'http://recit.herokuapp.com/c/view-invoice'
PRODUCT_INVENTORY_LINK = 'http://recit.herokuapp.com/c/product'
PRODUCT_INVENTORY_INVOICE_LINK = 'http://recit.herokuapp.com/c/product/invoice'

FREEMIUM_PLAN_LIMIT = 6
FREELANCE_PLAN_LIMIT = 5

# stripe plan id 

BUSINESS_PLAN_ID = 'plan_F4BBu1NgWJJpmI'
FREEMIUM_PLAN_ID = 'plan_F3ndLBPyWNBFHV'
FREELANCE_PLAN_ID = 'plan_F1uxsxSFIkvDCd'


"""
cloudinary.config( 
  cloud_name = "dos4bdnql", 
  api_key = config('CLOUDINARY_KEY'),
  api_secret = config('CLOUDINARY_SECRET_KEY')
)
"""

DEFAULT_CURRENCY= 'NGN'
ACCESS_KEY = config('ACCESS_KEY')
