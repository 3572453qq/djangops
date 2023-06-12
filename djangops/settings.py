"""
Django settings for djangops project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import json
import redis
from pathlib import Path
import os

import ldap
from django_auth_ldap.config import LDAPSearch
from .local_settings import *

# import mimetypes
# mimetypes.add_type("text/html", ".css", True)
# mimetypes.add_type("text/css", ".css", True)

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = 'ldap://192.168.1.70'
AUTH_LDAP_AUTHORIZE_ALL_USERS = True
# AUTH_LDAP_BIND_DN = u'CN=test01,OU=智能化促进中心,OU=集团总部,OU=Genzon,DC=genzon,DC=com,DC=cn'
# AUTH_LDAP_BIND_PASSWORD = "GenZon123"
AUTH_LDAP_BIND_DN = u'CN=userset,OU=智能化促进中心,OU=集团总部,OU=Genzon,DC=genzon,DC=com,DC=cn'
AUTH_LDAP_BIND_PASSWORD = "Genzon#234"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    u"OU=Genzon,DC=genzon,DC=com,DC=cn", ldap.SCOPE_SUBTREE, "(samAccountName=%(user)s)")
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xt$m=so0w!nj%ror%@r$)r43%8r=d7@tj8e-19e4872tu+7ap9'
# SECRET_KEY = '33333333333333333333333333'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'easyops',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangops.urls'

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

print(TEMPLATE_PATH)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_PATH],
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
print('1')

WSGI_APPLICATION = 'djangops.wsgi.application'
ASGI_APPLICATION = 'djangops.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangops',
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

print(2)

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
# STATIC_ROOT = 'static'
STATICFILES_DIRS = (
    STATIC_PATH,
)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login'

LOGIN_REDIRECT_URL = '/easyops/index'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60*30  # 30分钟
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
print(3)

WORKER_COUNT = 5
CMDB_MODELS = ('dbconnection', 'app', 'adminsql',
               'sqlstatement', 'ansibletasks', 'grafanareports')

rds = redis.Redis(host='127.0.0.1', port=6379)
# chatconsumer的worker设置
for i in range(WORKER_COUNT):
    rds.set('c'+str(i), 0)
# acconsumer的worker设置
for i in range(5, 5+WORKER_COUNT):
    rds.set('c'+str(i), 0)

rds.set('cone', 0)
rds.set('ctwo', 0)
rds.set('cthree', 0)
