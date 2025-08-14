from django.contrib import admin
from .models import Game, Move
# ======================================================================================================================
# مدیریت مدل Game در پنل ادمین
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'status', 'turn', 'created_date', 'updated_date')  # ستون‌های نمایش داده شده
    list_filter = ('status', 'turn', 'created_date')  # فیلترهای سمت راست ادمین
    search_fields = ('player__username',)  # امکان جستجو بر اساس نام کاربر
# ======================================================================================================================
# مدیریت مدل Move در پنل ادمین
@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'player', 'position', 'created_date','updated_date')  # ستون‌های نمایش داده شده
    list_filter = ('player', 'created_date')  # فیلترهای سمت راست ادمین
    search_fields = ('game__id', 'player')  # امکان جستجو بر اساس بازی یا بازیکن
# ======================================================================================================================