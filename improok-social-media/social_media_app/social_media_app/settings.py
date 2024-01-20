"""
Django settings for social_media_app project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# TuanTran's import & configure
import pymysql
from celery.schedules import crontab

pymysql.install_as_MySQLdb()

AUTH_USER_MODEL = 'social_media.User'

CORS_ALLOW_ALL_ORIGINS = True

# Tạm thời không dùng cái upload file bằng ckeditor
CKEDITOR_UPLOAD_PATH = "ckeditor/images/"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = '%s/social_media/static/' % BASE_DIR

INTERNAL_IPS = [
    "127.0.0.1",
]

import cloudinary

cloudinary.config(
    cloud_name='dhwuwy0to',
    api_key='569153767496484',
    api_secret='ghXq0iY8RhWbqBcJaide7W-34RY'
)

REST_FRAMEWORK = {
    # 'DEFAULT_PARSER_CLASSES': [
    #     'rest_framework.parsers.JSONParser',
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}

# Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Oauth2
CLIENT_ID = 'zDnklZ6ztQVU0X4DOQEymwV96MfWhW3Hk2VHq3D9'
CLIENT_SECRET = 'Wo2j1Qn6UKI691i30hmc4gZ7JCTazZ18KXNne7n2IYihCYoEw3PozWTtPc0CkiKZHtMBxOFTWISj83R5cSODQbCh9uTmNb5eefA4W9TwZmzI0D0smpz6bBf8CgSNnYDj'
#

# Send mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'trandangtuan0168@gmail.com'
EMAIL_HOST_PASSWORD = 'wojkawcuhoeltqws'
EMAIL_USE_TLS = True  # or False if not using TLS/SSL
DEFAULT_FROM_EMAIL = 'trandangtuan0168@gmail.com'

# Celery
# Message Broker (Tiện có redis xài luôn redis, khỏi RabbitMQ)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

# Đặt danh sách các tasks mà Celery sẽ tìm kiếm và đăng ký
CELERY_IMPORTS = (
    'social_media.tasks',
)

CELERY_IMPORTS = ('social_media.tasks',)
# CELERY_BEAT_SCHEDULE = app.conf.beat_schedule

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'celery': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/social_media/celery_task_log.log' % BASE_DIR,
            # 'filename': 'D:/celery.log',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

ASGI_APPLICATION = "social_media_app.asgi.application"
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*g4ng#+=tnw8lo07@1qsxb72f+306^po*(9(^y49adhv*8(9d-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.6',
    '127.0.0.1',
    '172.16.17.232',
    '192.168.1.27',
    '10.17.49.217',
    '*'
]

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_media.apps.SocialMediaConfig',
    'ckeditor',
    'ckeditor_uploader',
    'debug_toolbar',
    'rest_framework',
    'drf_yasg',
    'oauth2_provider',
    'corsheaders',
    'django_celery_results',
    'django_celery_beat',
    'channels',
    'channels_redis',
    'celery'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'social_media.middleware.ip_middleware.IPFilterMiddleWare',
    'social_media.middleware.characters_middleware.BlockInvalidCharactersMiddleware',
    'social_media.middleware.oauth2_middleware.Oauth2MiddleWare',
]

ROOT_URLCONF = 'social_media_app.urls'

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

WSGI_APPLICATION = 'social_media_app.wsgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'improok-social-media',
        'USER': 'root',
        'PASSWORD': 'Admin@123',
        'HOST': ''  # mặc định localhost
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
