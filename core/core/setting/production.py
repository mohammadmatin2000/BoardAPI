from ..settings import *
# ======================================================================================================================
# کلید امنیتی و حالت توسعه
SECRET_KEY = config("DJANGO_SECRET_KEY", default="unsafe-secret-key")  # بهتره در production از env استفاده کنید
DEBUG = True  # در production حتما False شود
ALLOWED_HOSTS = ["*"]  # در production باید دامنه‌های مجاز مشخص شوند
# ======================================================================================================================
# تنظیمات دیتابیس PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("PG_NAME", default="default_database"),
        "USER": config("PG_USER", default="username"),
        "PASSWORD": config("PG_PASSWORD", default="password"),
        "HOST": config("PG_HOST", default="db"),  # نام سرویس دیتابیس در docker-compose
        "PORT": config("PG_PORT", cast=int, default=5432),
    }
}
# ======================================================================================================================
# فعال‌سازی HSTS برای جلوگیری از حملات Man-in-the-Middle (مدت زمان 1 ساعت)
SECURE_HSTS_SECONDS = 3600
# ریدایرکت خودکار تمام درخواست‌ها از HTTP به HTTPS
SECURE_SSL_REDIRECT = True
# فعال‌سازی کوکی‌های امن فقط برای اتصال‌های HTTPS در نشست کاربران
SESSION_COOKIE_SECURE = True
# فعال‌سازی کوکی امن برای CSRF فقط روی HTTPS
CSRF_COOKIE_SECURE = True
# برای توسعه فعال است، در production محدود شود
CORS_ALLOW_ALL_ORIGINS = True
# ======================================================================================================================