"""
Django settings for dashboard_project project.
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom Apps
    'accounts',
    'core',
    'analytics',
    'ml_engine',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dashboard_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'dashboard_project.wsgi.application'

# Database - MySQL
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='mysql://root:Bsp@2026@127.0.0.1:3306/bsp_dashboard_db')
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files (Uploaded datasets & models)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email Settings (Testing ke liye console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'bsp-dashboard@noreply.com'

# CSRF Trusted Origins (Render.com ke liye)
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']


# ============================================================
# 🟢 JAZZMIN ADMIN PANEL CONFIGURATION
# ============================================================

JAZZMIN_SETTINGS = {
    "site_title": "BSP Dashboard Admin",
    "site_header": "BSP Dashboard",
    "site_brand": "🏭 BSP Dashboard",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to BSP Dashboard Administration",
    "copyright": "Bhilai Steel Plant © 2026",
    "search_model": ["auth.User", "core.Dataset", "core.ImageDataset", "core.AudioDataset", "core.VideoDataset"],

    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Main Dashboard", "url": "/", "new_window": False},
        {"name": "Datasets", "model": "core.Dataset"},
        {"name": "Users", "model": "auth.User"},
    ],

    "usermenu_links": [
        {"name": "Main Dashboard", "url": "/", "new_window": False},
        {"model": "auth.user"}
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "core", "core.Dataset", "core.ImageDataset", "core.AudioDataset", "core.VideoDataset", "core.MLModel", "core.Report"],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Dataset": "fas fa-database",
        "core.ImageDataset": "fas fa-image",
        "core.AudioDataset": "fas fa-microphone",
        "core.VideoDataset": "fas fa-video",
        "core.MLModel": "fas fa-brain",
        "core.Report": "fas fa-file-pdf",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": True,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
    "language_chooser": False,
}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# ============================================================
# 🟢 CELERY CONFIGURATION (Background Tasks)
# ============================================================

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_IMPORTS = ('core.tasks',)

# 🟢 Cache (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}


# ============================================================
# 🟢 SENTRY ERROR TRACKING
# ============================================================

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT', default='development')
SENTRY_TRACES_SAMPLE_RATE = config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
    )