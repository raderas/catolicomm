from .base import *

DEBUG = True

SECRET_KEY = 'django-insecure-2#q4_o7x_%_=v1#60!_sl+6pl+bkf=^&@z(1s8goe0$8$3&50e'
# SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}