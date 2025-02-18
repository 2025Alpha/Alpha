"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os, environ

# .env 파일을 읽기 위한 객체 생성
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# env 파일을 읽습니다. 최상위 폴더 기준 바로 아래에 위치한 .env 파일을 읽습니다.
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# env 파일로부터 rest api 키를 가져옵니다.
KAKAO_REST_API_KEY = env('KAKAO_REST_API_KEY')
KAKAO_AUTH_CODE = env('KAKAO_AUTH_CODE') # 카카오 로그인의 임시 인가코드를 사용됩니다. 테스트를 위해 사용됩니다.
KAKAO_REFRESH_TOKEN = env('KAKAO_REFRESH_TOKEN')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ppdx8t7r7ys%84627-7v9st+7+-@js620k#9ivbhc2)#0g-rhd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# TODO 특정 호스트만 접속 가능하도록 변경
ALLOWED_HOSTS = ['*'] # 모든 호스트 접속이 가능합니다.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'authenticate',
    'usr',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # cors 관련 미들웨어 추가
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# TODO 특정 호스트만 접속하도록 허용할것
CORS_ORIGIN_ALLOW_ALL = True # 모든 호스트의 접속을 허용합니다.
# CORS_ORIGIN_WHITELIST = () # 특정 호스트의 접속만을 허용합니다.

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr' # 언어를 한국어로 설정

TIME_ZONE = 'Asia/Seoul' # 타임존을 한국 시간으로 설정

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 아래는 커스텀 설정입니다.
AUTH_USER_MODEL = 'usr.User' # usr의 User를 기본 auth 모델로 적용