from pathlib import Path
from decouple import config, UndefinedValueError

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config("DEBUG", default=True, cast=bool)

try:
    SECRET_KEY = config("SECRET_KEY")
except UndefinedValueError:
    if DEBUG:
        SECRET_KEY = "----secret-dev-key----"
    else:
        raise RuntimeError("Missing SECRET_KEY environment variable")

ALLOWED_HOSTS = ["*"] if DEBUG else ["heidegger.delve.nu"]

URL_PREFIX = "index/"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "heidegger_index",
    "django_extensions",
    "markdownify_filter",
    "fullurl",
    "compressor",
    "theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = "heidegger_index.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "heidegger_index.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True
SUPPORTED_LOCALES = ["nl"]
LOCALE_PATHS = [BASE_DIR / "locales"]
LOCALE_IGNORE_PATTERNS = ["venv"]

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_URL = f"/{URL_PREFIX}static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CITEPROC_ENDPOINT = "https://citeproc.delve.nu"
CITEPROC_STYLE = "mhra"

INDEX_DIR = BASE_DIR / "index"
WORK_REFS_FILE = INDEX_DIR / "works.yml"
INDEX_FILE = INDEX_DIR / "heidegger-index.yml"
DESCRIPTIONS_DIR = BASE_DIR / "index" / "descriptions"

PAGINATION_WINDOW = 3

COMPRESS_OUTPUT_DIR = "/"
COMPRESS_PRECOMPILERS = [("text/x-scss", "django_libsass.SassCompiler")]
COMPRESS_OFFLINE = True
