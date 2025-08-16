from django.contrib import admin
from .models import Game, Move

# ======================================================================================================================
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'player_name', 'current_turn', 'is_finished',
        'first_hit', 'first_borne', 'second_hit', 'second_borne',
        'created_date', 'updated_date'
    )
    list_filter = (
        'current_turn', 'is_finished',
        'created_date', 'updated_date'
    )
    search_fields = ('player_name',)

# ======================================================================================================================
@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'player', 'move_data', 'created_date', 'updated_date')
    list_filter = ('player', 'created_date', 'updated_date')
    search_fields = ('game__id',)
# ======================================================================================================================