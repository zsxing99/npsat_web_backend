import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'MAKE_ME_A_SAFE_CRYPTOGRAPHICALLY_SECURE_SEED_VALUE'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
