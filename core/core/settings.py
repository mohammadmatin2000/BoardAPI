from pathlib import Path
from decouple import config

# ======================================================================================================================
# مسیر پایه پروژه
BASE_DIR = Path(__file__).resolve().parent.parent
# ======================================================================================================================
# اپلیکیشن‌های نصب شده
INSTALLED_APPS = [
    "django.contrib.admin",  # پنل مدیریت Django
    "django.contrib.auth",  # مدیریت کاربران و احراز هویت
    "django.contrib.contenttypes",  # مدیریت مدل‌ها و محتوا
    "django.contrib.sessions",  # مدیریت session ها
    "django.contrib.messages",  # پیام‌های فریمورک
    "django.contrib.staticfiles",  # مدیریت فایل‌های استاتیک
    "rest_framework",  # فریمورک API
    "drf_yasg",  # مستندسازی API
    "corsheaders",  # مدیریت CORS
    "game",  # اپلیکیشن داخلی پروژه
]
# ======================================================================================================================
# میدلور‌ها
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # امنیت پایه
    "corsheaders.middleware.CorsMiddleware",  # فعال‌سازی CORS
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# ======================================================================================================================
# فایل‌های URL و قالب‌ها
ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # مسیر قالب‌های پروژه
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
# ======================================================================================================================
WSGI_APPLICATION = "core.wsgi.application"
# ======================================================================================================================
# اعتبارسنجی پسورد کاربران
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]
# ======================================================================================================================
# تنظیمات بین‌المللی
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
# ======================================================================================================================
# فایل‌های استاتیک و رسانه
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]  # مسیرهای اضافی استاتیک
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# ======================================================================================================================
# نوع پیش‌فرض کلید اصلی مدل‌ها
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# ======================================================================================================================
# تنظیمات CORS
CORS_ALLOW_ALL_ORIGINS = True  # برای توسعه فعال است، در production محدود شود
# ======================================================================================================================
