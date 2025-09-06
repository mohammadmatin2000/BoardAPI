from rest_framework import serializers
from .models import Game, Move
# ======================================================================================================================
class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = ['id', 'player', 'move_data', 'created_date', 'updated_date']
# ======================================================================================================================
class GameSerializer(serializers.ModelSerializer):
    moves = MoveSerializer(many=True, read_only=True)
    class Meta:
        model = Game
        fields = ['id', 'player_name', 'board_state', 'current_turn','opponent_name', 'is_finished', 'created_date', 'moves']
# ======================================================================================================================