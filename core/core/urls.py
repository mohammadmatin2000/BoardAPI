from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ======================================================================================================================
# تنظیم و ساخت مستندات Swagger و Redoc برای API
schema_view = get_schema_view(
    openapi.Info(
        title="Flower Shop API",  # عنوان API
        default_version="v1",  # نسخه API
        description="بازی تخت",  # توضیح کوتاه
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # همه اجازه دسترسی دارند
)
# ======================================================================================================================
# آدرس‌دهی URLها
urlpatterns = [
    path("admin/", admin.site.urls),  # پنل مدیریت Django
    path("game/", include("game.urls")),  # URLهای اپلیکیشن game
    # مسیر JSON مستندات API بدون UI
    path(
        "swagger.<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    # صفحه مستندات Swagger UI
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # صفحه مستندات Redoc
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
# ======================================================================================================================
# اضافه کردن فایل‌های استاتیک و رسانه در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
# ======================================================================================================================
