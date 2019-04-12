import pathlib
import pymysql

pymysql.install_as_MySQLdb()
BASE_DIR = pathlib.Path(__file__).parent.parent

ansible_bin_path = '/usr/local/bin/ansible'
ks_url = 'http://192.168.1.249:8080/file/ks.cfg'
iso_url = 'http://192.168.1.249:8080/centos7/'
role = BASE_DIR / 'role'

DATABASES = {'default': {}}
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = str(BASE_DIR / 'db.sqlite3')

BROKER_URL = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

DEBUG = True
ALLOWED_HOSTS = ["*"]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
WSGI_APPLICATION = 'auto_deploy.wsgi.application'
ROOT_URLCONF = 'auto_deploy.urls'
SECRET_KEY = '1m0p)(e!4if263sf)oakbonhrm@5yd%x9m&b)@++2lpg7a10jm'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vm',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "vmManager" / "dist"],
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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]
