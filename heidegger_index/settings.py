from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = int(os.environ.get("DEBUG", 1))

try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError:
    if DEBUG:
        SECRET_KEY = "---some---lengthy---dev---key---"
    else:
        raise RuntimeError("Missing SECRET_KEY environment variable")

ALLOWED_HOSTS = ["heidegger.delve.nu", "delve.nu", "localhost"]

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
    "django_tailwind",
    "markdownify_filter",
    "fullurl",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
                "django_tailwind.context_processors.tailwind_classes",
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

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [BASE_DIR / "tailwind" / "dist"]

STATIC_URL = f"/{URL_PREFIX}static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CITEPROC_ENDPOINT = "https://labs.brill.com/citeproc"
CITEPROC_STYLE = "mhra"

INDEX_DIR = BASE_DIR / "index"
WORK_REFS_FILE = INDEX_DIR / "works.yml"
INDEX_FILE = INDEX_DIR / "heidegger-index.yml"
DESCRIPTIONS_DIR = BASE_DIR / "index" / "descriptions"

TAILWIND_STYLES_SRC_PATH = BASE_DIR / "tailwind" / "src" / "styles.css"
TAILWIND_STYLES_DIST_PATH = BASE_DIR / "tailwind" / "dist" / "styles.css"

TAILWIND_CLASSES = {
    "link_decoration": "font-semibold text-black underline decoration-sky-300 dark:text-white",
    "hidden_link_decoration": "font-semibold text-black underline transition-colors duration-300 decoration-transparent hover:decoration-sky-300 dark:text-white",
    "hidden_link_decoration_medium": "font-medium text-black underline transition-colors duration-300 decoration-transparent hover:decoration-sky-300 dark:text-white",
    "body_text": "text-slate-700 dark:text-slate-300",
    "description_prose": "prose prose-xl prose-slate dark:prose-invert prose-blockquote:not-italic prose-p:leading-normal dark:prose-blockquote:border-l-slate-600 prose-a:decoration-sky-300",
    "source_text": "prose prose-xl prose-slate dark:prose-invert prose-p:leading-snug prose-a:decoration-sky-300",
}

PAGINATION_WINDOW = 5
