# -*- coding: utf-8 -*-
"""
Django settings for swarm project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import sys
import datetime
from bin.configuration import conf as settings
from bin import configuration as conf
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNMODE = settings.get('core', 'run_mode').strip("'\"")
SWARM_LOG = os.path.join(os.path.expanduser(conf.SWARM_LOG),
                         "swarm-webserver-{}.log".format(RUNMODE.lower()))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'f^vpavbiaroy(-8@#65$-0j!xa@e+6rgclyg!9&enlup$t+j_1'
SECRET_KEY = settings.get('webserver', 'secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if settings.get('core', 'run_mode').upper() == 'DEBUG' else False

ALLOWED_HOSTS = ['*']

APPEND_SLASH = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'sscobbler.apps.SscobblerConfig',
    'sshostmgt.apps.SshostmgtConfig',
    'sscluster.apps.SsclusterConfig',
    'sscobweb.apps.SscobwebConfig',
    'account.apps.AccountConfig',
    'grafana.apps.GrafanaConfig',
    'swarm',
    'django_celery_beat',
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

# Add CORS
if settings.get('webserver', 'enable_cors') in ('True', 'true', 'T', 't'):
    INSTALLED_APPS.insert(0, 'corsheaders')
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
    CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'swarm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'sscobbler/templates/sscobbler')],
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

WSGI_APPLICATION = 'wsgi.application'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'swarm.exceptions.custom_exception_handler',
}

if settings.getboolean('core', 'enable_auth'):
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'].append('rest_framework.permissions.IsAuthenticated')

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'JSON_EDITOR': True,
    'SHOW_REQUEST_HEADERS': True,
}

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'


JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer'
}

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

swarm_db_engine = settings.get('core', 'swarm_db_engine')
if swarm_db_engine == 'django.db.backends.sqlite3':
    DATABASES_CONFIG = {
        'ENGINE': settings.get('core', 'swarm_db_engine'),
        'NAME': settings.get('core', 'swarm_db_name'),
    }
else:
    DATABASES_CONFIG = {
        'ENGINE': settings.get('core', 'swarm_db_engine'),
        'NAME': settings.get('core', 'swarm_db_name'),
        'USER': settings.get('core', 'swarm_db_user'),
        'PASSWORD': settings.get('core', 'swarm_db_password'),
        # Or an IP Address that your DB is hosted on
        'HOST': settings.get('core', 'swarm_db_host'),
        'PORT': settings.get('core', 'swarm_db_port'),
    }


DATABASES = {
    'default': DATABASES_CONFIG
}

TESTS_IN_PROGRESS = False
TEST_MODE = 'test' in sys.argv[1:] or 'jenkins' in sys.argv[1:]
if TEST_MODE:
    # 单元测试时, 跳过migrate, 极大的提升测试运行效率
    # 具体可以查看
    # https://simpleisbetterthancomplex.com/tips/2016/08/19/django-tip-12-disabling-migrations-to-speed-up-unit-tests.html
    # https://stackoverflow.com/questions/36487961/django-unit-testing-taking-a-very-long-time-to-create-test-database

    class DisableMigrations(object):
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    DEBUG = False
    TEMPLATE_DEBUG = False
    TESTS_IN_PROGRESS = True
    MIGRATION_MODULES = DisableMigrations()
else:
    MIGRATION_MODULES = {

    }

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'swarm', 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = os.path.join(settings.get(
    'core', 'swarm_home'), 'cobbler_sessions')

if not os.path.isdir(SESSION_FILE_PATH):
    os.mkdir(SESSION_FILE_PATH)


def get_loggers(level):
    loggers = {}
    for logger in ('django', 'sscluster', 'sshostmgt', 'sscobweb'):
        loggers.update({
            logger: {
                'handlers': ['file', 'stream'],
                'level': level,
                'propagate': True,
            }
        })
    return loggers


if not TEST_MODE:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s:'
                          '%(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': RUNMODE.upper(),
                'class': 'logging.FileHandler',
                'filename': '%s' % SWARM_LOG,
                'formatter': 'verbose'
            },
            'stream': {
                'level': RUNMODE.upper(),
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': get_loggers(RUNMODE.upper()),
    }


# Celery Configuration
CELERY_BROKER_URL = conf.get('celery', 'broker_url')
CELERY_ACCEPT_CONTENT = [conf.get('celery', 'accept_content')]
CELERY_RESULT_BACKEND = conf.get('celery', 'result_backend')
CELERY_TASK_SERIALIZER = conf.get('celery', 'task_serializer')


# Timezone
CELERY_TIMEZONE = 'Asia/Shanghai'    # 指定时区，不指定默认为 'UTC'

# schedules
# CELERY_BEAT_SCHEDULE = {
#     'add-every-60-seconds': {
#          'task': 'ssadvisor.tasks.loop_submit_job',
#          'schedule': crontab(minute='*/1'),       # 每 60 秒执行一次
#     },
# }
